from django import forms
from .models import FoodItem, Workout

# FoodItemForm for selecting food and entering quantity
class FoodItemForm(forms.Form):
    food_item = forms.ModelChoiceField(
        queryset=FoodItem.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Select Food Item"
    )
    quantity = forms.FloatField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter quantity (in servings)'}),
        label="Quantity",
        min_value=0.1
    )

# WorkoutForm for selecting workout and entering duration
# class WorkoutForm(forms.Form):
#     name = forms.CharField(
#         widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter workout name'}),
#         label="Workout Name"
#     )
#     calories_burned = forms.FloatField(
#         widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Calories burned in 30 minutes'}),
#         label="Calories Burned (in 30 minutes)"
#     )

class WorkoutForm(forms.ModelForm):
    class Meta:
        model = Workout
        fields = ['name', 'calories_burned']  # Fields you want to include in the form

    # You can still customize the widgets if needed
    name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter workout name'}),
        label="Workout Name"
    )
    calories_burned = forms.FloatField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Calories burned in 30 minutes'}),
        label="Calories Burned (in 30 minutes)"
    )
