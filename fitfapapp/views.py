from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404

from .serializers import RegisterSerializer, FoodItemSerializer, WorkoutSerializer
from .models import DailyCalorieRecord, FoodItem, Workout, UserGoal
from django.db import models
from django.contrib.auth import authenticate, login, logout
from .forms import FoodItemForm, WorkoutForm
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.contrib.auth.hashers import make_password
from rest_framework import status
from .serializers import LoginSerializer
from django.utils.timezone import now, timedelta
from rest_framework.permissions import IsAuthenticated, AllowAny

# Home View
def home(request):
    return render(request, 'home.html', {'user': request.user})  # Render the home template

# Food Items List View
@login_required
def food_items_list(request):
    food_items = FoodItem.objects.filter(user=request.user)  # Fetch only the logged-in user's items
    return render(request, 'food_items_list.html', {'food_items_list': food_items})

@login_required
def workout_list(request):
    workouts = Workout.objects.filter(user=request.user)  # Show only logged-in user's workouts
    return render(request, 'workout_list.html', {'workouts': workouts})

# Add Food Item View
from django.shortcuts import render, redirect
from fitfapapp.models import FoodItem



def add_food_item(request):
    if request.method == 'POST':
        name = request.POST.get('name').strip().lower()  # Normalize name input
        calories = request.POST.get('calories')
        unit_type = request.POST.get('unit_type')  # Capture unit type

        if not name or not calories or not unit_type:
            messages.error(request, "All fields are required.")
            return redirect('add_food_item')

        try:
            calories = float(calories)  # Convert to float
        except ValueError:
            messages.error(request, "Invalid calorie input. Please enter a number.")
            return redirect('add_food_item')
        # Check if the food item already exists for the user
        if FoodItem.objects.filter(user=request.user, name__iexact=name).exists():
            messages.error(request, "Item already exists!")
            return redirect('add_food_item')  # Stay on the form page
        
        # If item is unique, create and save it
        FoodItem.objects.create(user=request.user, name=name, calories=calories, unit_type=unit_type)
        messages.success(request, "Food item added successfully!")

        return redirect('food_items_list')  # Redirect to food list
    
    return render(request, 'add_food_item.html', {'unit_types': ['count', 'g', 'ml']})

@login_required
def delete_food_item(request, item_id):
    food_item = get_object_or_404(FoodItem, id=item_id, user=request.user)
    food_item.delete()
    return redirect('food_items_list')

@login_required
def delete_workout(request, workout_id):
    workout = get_object_or_404(Workout, id=workout_id, user=request.user)
    workout.delete()
    return redirect('workout_list')



@login_required  # Ensure only logged-in users can add workouts
def add_workout(request):
    if request.method == 'POST':
        form = WorkoutForm(request.POST)
        if form.is_valid():
            workout_name = form.cleaned_data['name']

            # Check if the workout already exists for the user
            if Workout.objects.filter(user=request.user, name=workout_name).exists():
                messages.error(request, f"You have already added '{workout_name}' workout!")
            else:
                workout = form.save(commit=False)  # Do not save yet
                workout.user = request.user  # Assign the logged-in user
                workout.save()  # Now save with user info
                messages.success(request, "Workout added successfully!")
                return redirect('workout_list')  # Adjust as needed
    else:
        form = WorkoutForm()

    return render(request, 'add_workout.html', {'form': form})

# Calorie Calculator View
from django.shortcuts import render
from .models import FoodItem, Workout
from .forms import FoodItemForm, WorkoutForm



@login_required
def calorie_calculator(request):
    if not request.user.is_authenticated:
        return redirect('login')  # Redirect if user is not logged in

    total_calories_intake = 0
    total_calories_burnt = 0

    # Fetch the user's goal (if set)
    user_goal = UserGoal.objects.filter(user=request.user).first()

    # Fetch only the logged-in user's data
    food_items = FoodItem.objects.filter(user=request.user)
    workouts = Workout.objects.filter(user=request.user)

    selected_foods = []
    selected_workouts = []

    if request.method == "POST":
        # Handle Food Intake
        food_ids = request.POST.getlist('food_item[]')
        quantities = request.POST.getlist('quantity[]')

        for food_id, quantity in zip(food_ids, quantities):
            try:
                food = FoodItem.objects.get(id=food_id, user=request.user)  # Ensure the item belongs to the user
                quantity = float(quantity)

                if quantity <= 0:
                    continue  # Ignore zero or negative quantities

                # Calculate calorie intake based on unit type
                if food.unit_type == 'g':  # Calories per 100g
                    adjusted_calories = (food.calories / 100) * quantity
                elif food.unit_type == 'ml':  # Calories per 100ml
                    adjusted_calories = (food.calories / 100) * quantity
                else:  # Count-based calculation
                    adjusted_calories = food.calories * quantity

                selected_foods.append({
                    'food': food,
                    'quantity': quantity,
                    'adjusted_calories': round(adjusted_calories, 2)
                })
                total_calories_intake += adjusted_calories
            except (FoodItem.DoesNotExist, ValueError):
                messages.error(request, "Invalid food selection or quantity.")
                continue  # Ignore invalid selections

        # Handle Workouts
        workout_ids = request.POST.getlist('workout[]')
        durations = request.POST.getlist('duration[]')

        for workout_id, duration in zip(workout_ids, durations):
            try:
                workout = Workout.objects.get(id=workout_id, user=request.user)  # Ensure the workout belongs to the user
                duration = float(duration)

                if duration <= 0:
                    continue  # Ignore zero or negative durations

                calories_per_minute = workout.calories_burned / 30  # Assuming the base is per 30 minutes
                calories_burnt = calories_per_minute * duration

                selected_workouts.append({
                    'workout': workout,
                    'duration': duration,
                    'calories_burnt': round(calories_burnt, 2)
                })
                total_calories_burnt += calories_burnt
            except (Workout.DoesNotExist, ValueError):
                messages.error(request, "Invalid workout selection or duration.")
                continue  # Ignore invalid selections

    # Calculate Net Calories
    net_calories = total_calories_intake - total_calories_burnt

    goal_text = None
    if user_goal:
        goal_text = f"{user_goal.goal.replace('_', ' ').title()} at {user_goal.weight}kg"

    
    return render(request, 'calorie_calculator.html', {
        'food_items_list': food_items,
        'workouts': workouts,
        'selected_foods': selected_foods,
        'selected_workouts': selected_workouts,
        'total_calories_intake': round(total_calories_intake, 2),
        'total_calories_burnt': round(total_calories_burnt, 2),
        'net_calories': round(net_calories, 2),
        'user_goal': user_goal,  # Pass goal data to template
        'goal_text': goal_text,
    })


# Calories Summary View
def calories_summary(request):
    total_calories_consumed = FoodItem.objects.aggregate(total=models.Sum('calories'))['total'] or 0
    total_calories_burned = Workout.objects.aggregate(total=models.Sum('calories_burned'))['total'] or 0
    net_calories = total_calories_consumed - total_calories_burned
    return JsonResponse({
        'total_calories_consumed': total_calories_consumed,
        'total_calories_burned': total_calories_burned,
        'net_calories': net_calories,
    })

@api_view(['POST'])
@permission_classes([AllowAny])
def login_api(request):
    serializer = LoginSerializer(data=request.data)

    if serializer.is_valid():
        user = serializer.validated_data["user"]  # Extract user
        login(request, user)  # Log in user
        return Response({"message": "Login successful!"}, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def login_page(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'You are now logged in.')
            return redirect('home')  # Redirect to the home page
        else:
            messages.error(request, 'Invalid username or password.')
            return render(request, 'login.html')
    else:
        return render(request, 'login.html')


def Registration_page(request):
    if request.method == 'POST':
        # Collect data from the registration form
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirmpassword', '')
        
        
        
        # Validate password match
        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'register.html')

        # Check for existing username or email
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return render(request, 'register.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email is already registered.')
            return render(request, 'register.html')

        # Save the user to the database
        try:
            user = User.objects.create_user(username=username, email=email, password=password)
            user.save()
            messages.success(request, 'Registration successful! You can now log in.')
            return redirect('login')  # Redirect to the login page
        except Exception as e:
            messages.error(request, f'Error during registration: {e}')
            return render(request, 'register.html')

    return render(request, 'register.html')


@api_view(['POST'])
@permission_classes([AllowAny])
def register_api(request):
    serializer = RegisterSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response({'message': 'Registration successful!'}, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def food_item_list_api(request):
    items = FoodItem.objects.filter(user=request.user)
    serializer = FoodItemSerializer(items, many=True)
    return Response({"food_items": serializer.data}, status=200)

# ----------------------------
# Delete Food Item
# ----------------------------
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_food_item_api(request, id):
    try:
        item = FoodItem.objects.get(id=id, user=request.user)
        item.delete()
        return Response({"message": "Food item deleted successfully"}, status=204)
    except FoodItem.DoesNotExist:
        return Response({"error": "Food item not found"}, status=404)

# ----------------------------
# List Workout Items (user-specific)
# ----------------------------
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def workout_list_api(request):
    items = Workout.objects.filter(user=request.user)
    serializer = WorkoutSerializer(items, many=True)
    return Response({"workouts": serializer.data}, status=200)

# ----------------------------
# Delete Workout Item
# ----------------------------
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_workout_item_api(request, id):
    try:
        item = Workout.objects.get(id=id, user=request.user)
        item.delete()
        return Response({"message": "Workout item deleted successfully"}, status=204)
    except Workout.DoesNotExist:
        return Response({"error": "Workout item not found"}, status=404)
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_food_item_api(request):
    serializer = FoodItemSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user=request.user)  # assign current user
        return Response({"message": "Food item added successfully", "data": serializer.data}, status=201)
    return Response(serializer.errors, status=400)

# ----------------------------
# Add Workout Item
# ----------------------------
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_workout_item_api(request):
    serializer = WorkoutSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user=request.user)  # assign current user
        return Response({"message": "Workout item added successfully", "data": serializer.data}, status=201)
    return Response(serializer.errors, status=400)
    
def logout_user(request):
    logout(request)
    return redirect('home')

def save_daily_calories(request):
    if request.method == "POST":
        user = request.user
        total_calories_intake = float(request.POST.get('total_calories_intake', 0))
        total_calories_burnt = float(request.POST.get('total_calories_burnt', 0))

        daily_record, created = DailyCalorieRecord.objects.update_or_create(
            user=user,
            date=now().date(),
            defaults={'total_calories_intake': total_calories_intake, 'total_calories_burnt': total_calories_burnt}
        )

        return JsonResponse({"message": "Data saved successfully!"})

    return JsonResponse({"error": "Invalid request"}, status=400)


@login_required
def set_goal(request):
    user_goal = UserGoal.objects.filter(user=request.user).first()

    if request.method == 'POST':
        weight = request.POST.get('weight')
        goal = request.POST.get('goal')

        if not weight or not goal:
            return JsonResponse({'success': False, 'error': 'Both weight and goal are required.'}, status=400)

        try:
            weight = float(weight)
            if weight <= 0:
                return JsonResponse({'success': False, 'error': 'Weight must be a positive number.'}, status=400)
        except ValueError:
            return JsonResponse({'success': False, 'error': 'Invalid weight format.'}, status=400)

        
        user_goal, created = UserGoal.objects.get_or_create(
            user=request.user,
            defaults={'weight': weight, 'goal': goal}
        )

        if not created:
            # If goal already exists, update it
            user_goal.weight = weight
            user_goal.goal = goal
            user_goal.save()

        print(f"Saved goal for {request.user.username}: {user_goal.weight}kg, {user_goal.goal}")

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True})
        return redirect('calorie')

    # For GET request, send existing goal to template
    return render(request, 'set_goal.html', {
        'user_goal': user_goal
    })



from datetime import timedelta

def get_weekly_progress(request):
    user = request.user
    today = now().date()
    last_week = today - timedelta(days=6)

    # Create a dict with existing records
    records = DailyCalorieRecord.objects.filter(user=user, date__gte=last_week).order_by('date')
    record_dict = {r.date: r.net_calories for r in records}

    weekly_data = []
    net_weekly_calories = 0

    for i in range(7):
        current_day = last_week + timedelta(days=i)
        net_cal = record_dict.get(current_day, 0)
        weekly_data.append({
            "day": f"Day {i+1}",
            "net_calories": net_cal
        })
        net_weekly_calories += net_cal

    # Fetch actual user goal
    user_goal_obj = UserGoal.objects.filter(user=user).first()
    user_goal = user_goal_obj.goal if user_goal_obj else "maintain"

    # Determine progress
    progress_status = "Good" if (
        (user_goal == "gain" and net_weekly_calories > 0) or 
        (user_goal == "lose" and net_weekly_calories < 0) or 
        (user_goal == "maintain" and abs(net_weekly_calories) < 500)
    ) else "Bad"

    return JsonResponse({
        "weekly_data": weekly_data,
        "progress_status": progress_status
    })
