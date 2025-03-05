

from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

class FoodItem(models.Model):
    UNIT_CHOICES = [
        ('count', 'Count'),
        ('g', 'Grams'),
        ('ml', 'Milliliters'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Link food to user
    name = models.CharField(max_length=255)
    calories = models.FloatField(help_text="Calories per unit (100g, 100ml, or per count)")
    unit_type = models.CharField(max_length=10, choices=UNIT_CHOICES, default='count')

    def __str__(self):
        return f"{self.name} - {self.calories} cal/{self.unit_type}"  # Show food name with user

class Workout(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Link workout to user
    name = models.CharField(max_length=255)
    calories_burned = models.FloatField()

    def __str__(self):
        return f"{self.name} ({self.user.username})"  # Show workout name with user

    def calories_burnt(self, duration):
        return self.calories_burned * duration  # Adjust calories by duration

class UserGoal(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    weight = models.FloatField()
    goal = models.CharField(max_length=50, choices=[
        ('weight_gain', 'Weight Gain'),
        ('weight_loss', 'Weight Loss'),
        ('maintain', 'Maintain Weight'),
    ])

    def __str__(self):
        return f"{self.user.username} - {self.goal}"

@receiver(post_save, sender=User)
def create_default_items(sender, instance, created, **kwargs):
    if created:  # Runs only when a new user is created
        default_foods = [
            {"name": "Apple", "calories": 52},
            {"name": "Banana", "calories": 89},
            {"name": "Rice", "calories": 130},
            {"name": "Chicken Breast", "calories": 165},
            {"name": "Egg", "calories": 78}
        ]
        default_workouts = [
            {"name": "Running", "calories_burned": 10},  # Per minute
            {"name": "Cycling", "calories_burned": 8},
            {"name": "Swimming", "calories_burned": 12},
            {"name": "Weight Training", "calories_burned": 6},
        ]

        for food in default_foods:
            FoodItem.objects.create(user=instance, name=food["name"], calories=food["calories"])

        for workout in default_workouts:
            Workout.objects.create(user=instance, name=workout["name"], calories_burned=workout["calories_burned"])

from django.db import models
from django.contrib.auth.models import User
from datetime import date

class DailyCalorieRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(default=date.today)
    total_calories_intake = models.FloatField()
    total_calories_burnt = models.FloatField()

    @property
    def net_calories(self):
        return self.total_calories_intake - self.total_calories_burnt
