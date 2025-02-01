from django.db import models

# Create your models here.
class FoodItem(models.Model):
    name = models.CharField(max_length=255)
    calories = models.FloatField()

    def __str__(self):
        return self.name


class Workout(models.Model):
    name = models.CharField(max_length=255)
    calories_burned = models.FloatField()

    def __str__(self):
        return self.name
    
    def calories_burnt(self, duration):
        # Adjust calories burned based on workout duration (if needed)
        return self.calories_burned * duration
    

