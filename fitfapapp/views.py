from django.http import JsonResponse
from django.shortcuts import render, redirect
from .models import FoodItem, Workout
from django.db import models
from django.contrib.auth import authenticate, login, logout
from .forms import FoodItemForm, WorkoutForm
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

# Home View
def home(request):
    return render(request, 'home.html', {'user': request.user})  # Render the home template

# Food Items List View
@login_required
def food_items_list(request):
    food_items = FoodItem.objects.filter(user=request.user)  # Fetch only the logged-in user's items
    return render(request, 'food_items_list.html', {'food_items': food_items})

@login_required
def workout_list(request):
    workouts = Workout.objects.filter(user=request.user)  # Show only logged-in user's workouts
    return render(request, 'workout_list.html', {'workouts': workouts})

# Add Food Item View
from django.shortcuts import render, redirect
from fitfapapp.models import FoodItem

@login_required  # Ensure only logged-in users can add food items
def add_food_item(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        calories = request.POST.get('calories')

        # Store food item under the logged-in user
        FoodItem.objects.create(user=request.user, name=name, calories=calories)

        return redirect('food_items_list')  # Adjust to your actual food items list view
    
    return render(request, 'add_food_item.html')


# Add Workout View
@login_required  # Ensure only logged-in users can add workouts
def add_workout(request):
    if request.method == 'POST':
        form = WorkoutForm(request.POST)
        if form.is_valid():
            workout = form.save(commit=False)  # Do not save yet
            workout.user = request.user  # Assign the logged-in user
            workout.save()  # Now save with user info
            return redirect('workout_list')  # Adjust as needed
    else:
        form = WorkoutForm()

    return render(request, 'add_workout.html', {'form': form})


# Calorie Calculator View
from django.shortcuts import render
from .models import FoodItem, Workout
from .forms import FoodItemForm, WorkoutForm

def calorie_calculator(request):
    total_calories_intake = 0
    total_calories_burnt = 0
    food_form = FoodItemForm(request.POST or None)
    workout_form = WorkoutForm(request.POST or None)

    if request.method == "POST":
        # Handle Food Form Submission
        if 'food_form_submit' in request.POST and food_form.is_valid():
            selected_food = food_form.cleaned_data['food_item']
            quantity = food_form.cleaned_data['quantity']
            total_calories_intake = selected_food.calories * quantity

        # Handle Workout Submission
        if 'workout_form_submit' in request.POST and workout_form.is_valid():
            selected_workout = workout_form.cleaned_data['workout']
            workout_duration = workout_form.cleaned_data['duration']
            calories_per_minute = selected_workout.calories_burned / 30  # Assuming 30 min workout duration as standard
            total_calories_burnt = calories_per_minute * workout_duration

    # Calculate net calories
    net_calories = total_calories_intake - total_calories_burnt

    return render(request, 'calorie_calculator.html', {
        'food_form': food_form,
        'workout_form': workout_form,
        'total_calories_intake': total_calories_intake,
        'total_calories_burnt': total_calories_burnt,
        'net_calories': net_calories,
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
# def Registration_page(request):
#     if request.method == 'POST':
#         username = request.POST['username']
#         email = request.POST['email']
#         password = request.POST['password']
#         confirm_password = request.POST['confirmpassword']
        
#         if password != confirm_password:
#             messages.error(request, 'Passwords do not match.')
#             return render(request, 'register.html')
        
#         try:
#             user = user.objects.create_user(username=username, email=email, password=password)
#             user.save()
#             messages.success(request, 'Your account has been created! You can now log in.')
#             return redirect('login')
#         except Exception as e:
#             messages.error(request, f'Error creating user: {e}')
#             return render(request, 'register.html')
#     else:
#         # GET request to display the registration form
#         return render(request, 'register.html')


def Registration_page(request):
    if request.method == 'POST':
        # Collect data from the registration form
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirmpassword']
        
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

    else:
        # Handle GET request by rendering the registration form
        return render(request, 'register.html')
    
def logout_user(request):
    logout(request)
    return redirect('home')
