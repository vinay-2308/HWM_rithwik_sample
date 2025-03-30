from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Exercise(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    video_url = models.URLField(blank=True, null=True)
    image = models.ImageField(upload_to='exercise_images/', blank=True, null=True)
    
    def __str__(self):
        return self.name

class WorkoutPlan(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='workout_plans')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"{self.name} - {self.user.username}"

class WorkoutDay(models.Model):
    plan = models.ForeignKey(WorkoutPlan, on_delete=models.CASCADE, related_name='workout_days')
    day_name = models.CharField(max_length=20)  # e.g., "Monday", "Day 1", etc.
    
    def __str__(self):
        return f"{self.plan.name} - {self.day_name}"

class WorkoutExercise(models.Model):
    workout_day = models.ForeignKey(WorkoutDay, on_delete=models.CASCADE, related_name='exercises')
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    sets = models.IntegerField(default=3)
    reps = models.IntegerField(default=10)
    rest_time = models.IntegerField(default=60)  # Rest time in seconds
    order = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.exercise.name} - {self.sets}x{self.reps}"

class WorkoutLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='workout_logs')
    workout_plan = models.ForeignKey(WorkoutPlan, on_delete=models.CASCADE)
    workout_day = models.ForeignKey(WorkoutDay, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    completed = models.BooleanField(default=False)
    duration = models.IntegerField(default=0)  # Duration in minutes
    
    def __str__(self):
        return f"{self.user.username} - {self.workout_day.day_name} - {self.date}"

class ExerciseLog(models.Model):
    workout_log = models.ForeignKey(WorkoutLog, on_delete=models.CASCADE, related_name='exercise_logs')
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    sets_completed = models.IntegerField(default=0)
    reps_completed = models.TextField(blank=True, null=True)  # Store as JSON string e.g. "[10, 8, 6]"
    weight_used = models.TextField(blank=True, null=True)  # Store as JSON string e.g. "[15, 15, 15]"
    notes = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.exercise.name} - {self.workout_log.date}"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    height = models.FloatField(blank=True, null=True)  # in cm
    weight = models.FloatField(blank=True, null=True)  # in kg
    fitness_goal = models.CharField(max_length=100, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    preferred_theme = models.CharField(max_length=10, default='light')  # 'light' or 'dark'
    
    def __str__(self):
        return f"{self.user.username}'s Profile"