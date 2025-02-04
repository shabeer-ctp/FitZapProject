# from django.db import models

# # Create your models here.
# class FoodItem(models.Model):
#     name = models.CharField(max_length=255)
#     calories = models.FloatField()

#     def __str__(self):
#         return self.name


# class Workout(models.Model):
#     name = models.CharField(max_length=255)
#     calories_burned = models.FloatField()

#     def __str__(self):
#         return self.name
    
#     def calories_burnt(self, duration):
#         # Adjust calories burned based on workout duration (if needed)
#         return self.calories_burned * duration

from django.contrib.auth.models import User
from django.db import models

class FoodItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Link food to user
    name = models.CharField(max_length=255)
    calories = models.FloatField()

    def __str__(self):
        return f"{self.name} ({self.user.username})"  # Show food name with user

class Workout(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Link workout to user
    name = models.CharField(max_length=255)
    calories_burned = models.FloatField()

    def __str__(self):
        return f"{self.name} ({self.user.username})"  # Show workout name with user

    def calories_burnt(self, duration):
        return self.calories_burned * duration  # Adjust calories by duration

    

