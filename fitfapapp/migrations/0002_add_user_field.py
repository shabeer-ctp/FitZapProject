from django.db import migrations, models

def get_default_user(apps, schema_editor):
    User = apps.get_model('auth', 'User')  # Dynamically get the User model
    first_user = User.objects.first()  # Fetch the first user
    if first_user is None:
        raise Exception("No user exists. Create a user first!")
    return first_user  # Return the first User object

def set_default_user_for_existing_data(apps, schema_editor):
    FoodItem = apps.get_model('fitfapapp', 'FoodItem')
    Workout = apps.get_model('fitfapapp', 'Workout')
    User = apps.get_model('auth', 'User')
    
    first_user = User.objects.first()
    if first_user:
        FoodItem.objects.filter(user__isnull=True).update(user=first_user)
        Workout.objects.filter(user__isnull=True).update(user=first_user)

class Migration(migrations.Migration):

    dependencies = [
        ('fitfapapp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='fooditem',
            name='user',
            field=models.ForeignKey(to='auth.User', on_delete=models.CASCADE, null=True),
        ),
        migrations.AddField(
            model_name='workout',
            name='user',
            field=models.ForeignKey(to='auth.User', on_delete=models.CASCADE, null=True),
        ),
        migrations.RunPython(set_default_user_for_existing_data),
        migrations.AlterField(
            model_name='fooditem',
            name='user',
            field=models.ForeignKey(to='auth.User', on_delete=models.CASCADE, null=False),
        ),
        migrations.AlterField(
            model_name='workout',
            name='user',
            field=models.ForeignKey(to='auth.User', on_delete=models.CASCADE, null=False),
        ),
    ]

