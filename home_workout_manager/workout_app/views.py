import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import logout
from django.utils import timezone
from django.http import JsonResponse
from django.db.models import Count
from .forms import (
    UserRegisterForm, 
    UserUpdateForm,  # Add this import
    ProfileUpdateForm,  # Add this import 
    UserProfileForm, 
    WorkoutPlanForm, 
    WorkoutDayForm, 
    WorkoutExerciseForm, 
    ExerciseForm, 
    ExerciseLogForm
)
from .models import (
    WorkoutPlan,
    WorkoutDay,
    WorkoutExercise,
    WorkoutLog,
    ExerciseLog,
    Exercise,
    UserProfile
)

from .workout_utils import (
    get_user_stats, 
    get_exercise_progress, 
    calculate_volume_progress,
    suggest_workout,
    calculate_bmi,
    get_bmi_category
)


def custom_logout(request):
    """Custom logout view that supports both GET and POST methods"""
    if request.method == 'POST' or request.method == 'GET':
        logout(request)
        messages.success(request, 'You have been successfully logged out.')
        # If you want to show the logout template:
        return render(request, 'workout_app/logout.html')
        # Or if you want to redirect directly to login:
        # return redirect('login')
    else:
        return redirect('dashboard')

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create user profile
            UserProfile.objects.create(user=user)
            messages.success(request, f'Account created successfully. You can now log in.')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'workout_app/register.html', {'form': form})

@login_required
def dashboard(request):
    # Get user's workout plans
    workout_plans = WorkoutPlan.objects.filter(user=request.user)
    
    # Get recent workout logs
    recent_logs = WorkoutLog.objects.filter(user=request.user).order_by('-date')[:5]
    
    # Get today's workout if any
    today = timezone.now().date()
    today_workout = WorkoutLog.objects.filter(user=request.user, date=today).first()
    
    # Calculate stats
    total_workouts = WorkoutLog.objects.filter(user=request.user, completed=True).count()
    total_exercises = ExerciseLog.objects.filter(workout_log__user=request.user).count()
    
    # Streaks calculation
    consecutive_days = 0
    if total_workouts > 0:
        logs = WorkoutLog.objects.filter(user=request.user, completed=True).order_by('-date')
        if logs.first().date == today:
            consecutive_days = 1
            last_date = logs.first().date
            for log in logs[1:]:
                if (last_date - log.date).days == 1:
                    consecutive_days += 1
                    last_date = log.date
                else:
                    break
    
    context = {
        'workout_plans': workout_plans,
        'recent_logs': recent_logs,
        'today_workout': today_workout,
        'total_workouts': total_workouts,
        'total_exercises': total_exercises,
        'consecutive_days': consecutive_days
    }
    
    return render(request, 'workout_app/dashboard.html', context)

@login_required
def workout_plans(request):
    """View all workout plans and create new ones"""
    if request.method == 'POST':
        form = WorkoutPlanForm(request.POST)
        if form.is_valid():
            plan = form.save(commit=False)
            plan.user = request.user
            plan.save()
            messages.success(request, 'Workout plan created successfully!')
            return redirect('workout_plan_detail', pk=plan.pk)
    else:
        form = WorkoutPlanForm()
    
    plans = WorkoutPlan.objects.filter(user=request.user)
    
    context = {
        'plans': plans,
        'form': form
    }
    
    return render(request, 'workout_app/workout_plans.html', context)

@login_required
def workout_plan_detail(request, pk):
    """View and edit a specific workout plan"""
    plan = get_object_or_404(WorkoutPlan, pk=pk, user=request.user)
    workout_days = WorkoutDay.objects.filter(plan=plan)
    
    if request.method == 'POST':
        form = WorkoutDayForm(request.POST)
        if form.is_valid():
            day = form.save(commit=False)
            day.plan = plan
            day.save()
            messages.success(request, f'Added {day.day_name} to your plan!')
            return redirect('workout_plan_detail', pk=plan.pk)
    else:
        form = WorkoutDayForm()
    
    context = {
        'plan': plan,
        'workout_days': workout_days,
        'form': form
    }
    
    return render(request, 'workout_app/workout_plan_detail.html', context)

@login_required
def workout_day_detail(request, pk):
    """View and edit exercises for a specific workout day"""
    day = get_object_or_404(WorkoutDay, pk=pk)
    
    # Ensure user owns this workout day
    if day.plan.user != request.user:
        messages.error(request, "You don't have permission to view this workout day.")
        return redirect('dashboard')
    
    exercises = WorkoutExercise.objects.filter(workout_day=day).order_by('order')
    all_exercises = Exercise.objects.all()
    
    if request.method == 'POST':
        form = WorkoutExerciseForm(request.POST)
        if form.is_valid():
            workout_exercise = form.save(commit=False)
            workout_exercise.workout_day = day
            workout_exercise.order = exercises.count()  # Add to the end
            workout_exercise.save()
            messages.success(request, f'Added {workout_exercise.exercise.name} to your workout!')
            return redirect('workout_day_detail', pk=day.pk)
    else:
        form = WorkoutExerciseForm()
    
    context = {
        'day': day,
        'exercises': exercises,
        'all_exercises': all_exercises,
        'form': form
    }
    
    return render(request, 'workout_app/workout_day_detail.html', context)

@login_required
def delete_workout_exercise(request, pk):
    """Delete an exercise from a workout day"""
    exercise = get_object_or_404(WorkoutExercise, pk=pk)
    
    # Ensure user owns this exercise
    if exercise.workout_day.plan.user != request.user:
        messages.error(request, "You don't have permission to delete this exercise.")
        return redirect('dashboard')
    
    day_pk = exercise.workout_day.pk
    exercise.delete()
    messages.success(request, 'Exercise removed from workout.')
    return redirect('workout_day_detail', pk=day_pk)

@login_required
def exercise_library(request):
    """View all exercises and add new ones"""
    exercises = Exercise.objects.all()
    
    if request.method == 'POST':
        form = ExerciseForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Exercise added to library!')
            return redirect('exercise_library')
    else:
        form = ExerciseForm()
    
    context = {
        'exercises': exercises,
        'form': form
    }
    
    return render(request, 'workout_app/exercise_library.html', context)

@login_required
def exercise_detail(request, pk):
    """View details of a specific exercise"""
    exercise = get_object_or_404(Exercise, pk=pk)
    
    context = {
        'exercise': exercise
    }
    
    return render(request, 'workout_app/exercise_detail.html', context)

@login_required
def start_workout(request, day_pk=None):
    """Start a workout session from a specific day"""
    if day_pk:
        day = get_object_or_404(WorkoutDay, pk=day_pk)
        
        # Ensure user owns this workout day
        if day.plan.user != request.user:
            messages.error(request, "You don't have permission to access this workout.")
            return redirect('dashboard')
        
        # Check if workout already exists for today
        today = timezone.now().date()
        existing_log = WorkoutLog.objects.filter(
            user=request.user,
            workout_plan=day.plan,
            workout_day=day,
            date=today
        ).first()
        
        if existing_log:
            workout_log = existing_log
        else:
            # Create new workout log
            workout_log = WorkoutLog.objects.create(
                user=request.user,
                workout_plan=day.plan,
                workout_day=day,
                date=today
            )
            
            # Create exercise logs for each exercise in the workout day
            for exercise_item in WorkoutExercise.objects.filter(workout_day=day).order_by('order'):
                ExerciseLog.objects.create(
                    workout_log=workout_log,
                    exercise=exercise_item.exercise
                )
        
        return redirect('perform_workout', log_pk=workout_log.pk)
    
    # If no day_pk provided, show a list of workout plans to choose from
    plans = WorkoutPlan.objects.filter(user=request.user)
    context = {'plans': plans}
    return render(request, 'workout_app/start_workout.html', context)

@login_required
def perform_workout(request, log_pk):
    """Perform a workout session"""
    workout_log = get_object_or_404(WorkoutLog, pk=log_pk, user=request.user)
    exercise_logs = ExerciseLog.objects.filter(workout_log=workout_log)
    
    # Check if this is a POST request (workout completion)
    if request.method == 'POST':
        for exercise_log in exercise_logs:
            # Get form data for each exercise
            sets_completed = request.POST.get(f'sets_completed_{exercise_log.pk}', 0)
            reps_completed = request.POST.get(f'reps_completed_{exercise_log.pk}', '[]')
            weight_used = request.POST.get(f'weight_used_{exercise_log.pk}', '[]')
            notes = request.POST.get(f'notes_{exercise_log.pk}', '')
            
            # Update exercise log
            exercise_log.sets_completed = sets_completed
            exercise_log.reps_completed = reps_completed
            exercise_log.weight_used = weight_used
            exercise_log.notes = notes
            exercise_log.save()
        
        # Mark workout as completed
        duration = int(request.POST.get('workout_duration', 0))
        workout_log.completed = True
        workout_log.duration = duration
        workout_log.save()
        
        messages.success(request, 'Workout completed successfully!')
        return redirect('dashboard')
    
    # If not a POST request, display the workout
    context = {
        'workout_log': workout_log,
        'exercise_logs': exercise_logs
    }
    
    return render(request, 'workout_app/perform_workout.html', context)

@login_required
def workout(request):
    """Main workout view - shows recent and available workouts"""
    # Get user's workout plans
    plans = WorkoutPlan.objects.filter(user=request.user)
    
    # Get recent workout logs
    recent_logs = WorkoutLog.objects.filter(
        user=request.user
    ).order_by('-date')[:5]
    
    context = {
        'plans': plans,
        'recent_logs': recent_logs
    }
    
    return render(request, 'workout_app/workout.html', context)

@login_required
def progress(request):
    """View workout progress and statistics"""
    # Get all workout logs for the user
    workout_logs = WorkoutLog.objects.filter(user=request.user).order_by('-date')
    
    # Calculate weekly stats
    today = timezone.now().date()
    start_of_week = today - timezone.timedelta(days=today.weekday())
    workouts_this_week = workout_logs.filter(date__gte=start_of_week, completed=True).count()
    
    # Calculate monthly stats
    start_of_month = today.replace(day=1)
    workouts_this_month = workout_logs.filter(date__gte=start_of_month, completed=True).count()
    
    # Calculate all-time stats
    total_workouts = workout_logs.filter(completed=True).count()
    total_duration = sum(log.duration for log in workout_logs.filter(completed=True)) if total_workouts > 0 else 0
    avg_duration = total_duration / total_workouts if total_workouts > 0 else 0
    
    # Get most common workout
    most_common_workout = None
    if workout_logs.exists():
        most_common = workout_logs.values('workout_day__day_name').annotate(
            count=Count('workout_day__day_name')
        ).order_by('-count').first()
        if most_common:
            most_common_workout = most_common['workout_day__day_name']
    
    # Calculate workout distribution by day of week
    days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    workout_distribution = []
    
    for day in days_of_week:
        # Count workouts for each day
        count = workout_logs.filter(completed=True, date__week_day=get_weekday_number(day)).count()
        workout_distribution.append(count)
    
    context = {
        'workout_logs': workout_logs,
        'workouts_this_week': workouts_this_week,
        'workouts_this_month': workouts_this_month,
        'total_workouts': total_workouts,
        'total_duration': total_duration,
        'avg_duration': avg_duration,
        'most_common_workout': most_common_workout,
        'workout_distribution': workout_distribution
    }
    
    return render(request, 'workout_app/progress.html', context)

def get_weekday_number(day_name):
    """Convert day name to Django's week_day filter number (1=Sunday, 2=Monday, etc.)"""
    days = {
        'Monday': 2,
        'Tuesday': 3,
        'Wednesday': 4,
        'Thursday': 5,
        'Friday': 6,
        'Saturday': 7,
        'Sunday': 1
    }
    return days.get(day_name, 1)  # Default to Sunday if invalid name

@login_required
def settings(request):
    """User settings view to update profile and account information"""
    
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('settings')  # Redirect to refresh the page with new data
        else:
            # If form validation fails, show error messages
            for field, errors in user_form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
            
            for field, errors in profile_form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'profile': request.user.profile
    }
    
    return render(request, 'workout_app/settings.html', context)

@login_required
def delete_workout_plan(request, pk):
    """Delete a workout plan"""
    plan = get_object_or_404(WorkoutPlan, pk=pk, user=request.user)
    
    if request.method == 'POST':
        plan_name = plan.name  # Store name before deletion for the message
        plan.delete()
        messages.success(request, f'Workout plan "{plan_name}" deleted successfully!')
        return redirect('workout_plans')
    
    # If it's a GET request, render the confirmation template
    return render(request, 'workout_app/delete_workout_plan.html', {'plan': plan})


@login_required
def update_exercise_order(request):
    """AJAX view to update exercise order"""
    if request.method == 'POST':
        exercise_ids = json.loads(request.POST.get('exercise_ids', '[]'))
        
        # Update order for each exercise
        for index, exercise_id in enumerate(exercise_ids):
            exercise = WorkoutExercise.objects.get(pk=exercise_id)
            
            # Verify user has permission to modify this exercise
            if exercise.workout_day.plan.user != request.user:
                return JsonResponse({'status': 'error', 'message': 'Permission denied'})
            
            exercise.order = index
            exercise.save()
        
        return JsonResponse({'status': 'success'})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@login_required
def advanced_stats(request):
    """Comprehensive statistics view for user workout data"""
    # Get time period from request (default to 30 days)
    time_period = int(request.GET.get('period', 30))
    
    # Get user stats for specified period
    user_stats = get_user_stats(request.user, days=time_period)
    
    # Get BMI information
    user_profile = request.user.profile
    bmi = calculate_bmi(user_profile)
    bmi_category = get_bmi_category(bmi)
    
    # Get exercise selection for progress chart
    exercises = Exercise.objects.filter(
        exerciselog__workout_log__user=request.user,
        exerciselog__workout_log__completed=True
    ).distinct()
    
    selected_exercise_id = request.GET.get('exercise')
    
    # If exercise id is provided and valid, get progress data
    exercise_progress = None
    volume_progress = None
    
    if selected_exercise_id and exercises.filter(id=selected_exercise_id).exists():
        selected_exercise = exercises.get(id=selected_exercise_id)
        exercise_progress = get_exercise_progress(
            request.user, 
            selected_exercise_id, 
            days=time_period
        )
        
        # Calculate volume progress statistics
        volume_progress = calculate_volume_progress(exercise_progress)
    
    # Get workout suggestion for today
    suggested_workout = suggest_workout(request.user)
    
    context = {
        'user_stats': user_stats,
        'time_period': time_period,
        'bmi': bmi,
        'bmi_category': bmi_category,
        'exercises': exercises,
        'selected_exercise_id': selected_exercise_id,
        'exercise_progress': exercise_progress,
        'volume_progress': volume_progress,
        'suggested_workout': suggested_workout
    }
    
    return render(request, 'workout_app/advanced_stats.html', context)