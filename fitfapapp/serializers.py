from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate

from .models import FoodItem, Workout, DailyCalorieRecord, UserGoal

class RegisterSerializer(serializers.ModelSerializer):
    confirmpassword = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'confirmpassword']
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, data):
        if data['password'] != data['confirmpassword']:
            raise serializers.ValidationError({'password': 'Passwords do not match'})

        if User.objects.filter(username=data['username']).exists():
            raise serializers.ValidationError({'username': 'Username already exists'})

        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError({'email': 'Email is already registered'})

        return data

    def create(self, validated_data):
        validated_data.pop('confirmpassword')  # Remove confirm password
        validated_data['password'] = make_password(validated_data['password'])  # Hash password
        user = User.objects.create(**validated_data)
        return user

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            raise serializers.ValidationError("Both username and password are required.")

        user = authenticate(username=username, password=password)
        if not user:
            raise serializers.ValidationError("Invalid username or password.")

        data["user"] = user  # Store the user object to use in the view
        return data
    
# Food Item Serializer
class FoodItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodItem
        fields = ['id', 'name', 'calories', 'unit_type']

# Workout Serializer
class WorkoutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workout
        fields = ['id', 'name', 'calories_burned']
        
class DailyCalorieRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyCalorieRecord
        fields = ['total_calories_intake', 'total_calories_burnt']


class UserGoalSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserGoal
        fields = ['weight', 'goal']


# This one is optional (if you want to structure the response better)
class WeeklyProgressSerializer(serializers.Serializer):
    day = serializers.CharField()
    net_calories = serializers.FloatField()