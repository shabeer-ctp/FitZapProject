
from django.urls import path
from . import views
from .views import register_api, login_api

urlpatterns = [
    path('',views.home,name='home'),
    path('food-items/', views.food_items_list, name='food_items_list'),
    path('food-items/add/', views.add_food_item, name='add_food_item'),
    path('calories-summary/', views.calories_summary, name='calories_summary'),
    path('workouts/add/', views.add_workout, name='add_workout'),
    # path('workouts/calculate-burn/', views.calculate_workout_burn, name='calculate_workout_burn'),
    path('login/', views.login_page, name='login'),
    path('api/login/', login_api, name='login_api'),
    path('register/', views.Registration_page, name='register'),  # Renders the registration page
    path('api/register/', views.register_api, name='register_api'),
    path('calories/', views.calorie_calculator, name='calorie_calculator'),
    path('logout/', views.logout_user, name='logout'),
    path('workouts/', views.workout_list, name='workout_list'),

]