"""
Workout Utilities Library
------------------------
A set of utility functions to enhance the functionality of the home workout manager application.
Functions include:
- Workout statistics calculation
- Date and time conversion helpers
- Progress calculation
- Workout suggestion algorithms
"""

import json
import datetime
from django.utils import timezone
from django.db.models import Avg, Sum, Count, Max
from .models import WorkoutLog, ExerciseLog, WorkoutPlan, WorkoutDay, UserProfile

# ===== Workout Statistics Functions =====

def get_user_stats(user, days=30):
    """
    Get comprehensive workout statistics for a user over a specified period.
    
    Args:
        user: The User object
        days: Number of days to look back (default 30)
        
    Returns:
        dict: Dictionary containing various workout statistics
    """
    # Calculate date range
    end_date = timezone.now().date()
    start_date = end_date - datetime.timedelta(days=days)
    
    # Get relevant workout logs
    logs = WorkoutLog.objects.filter(
        user=user,
        date__gte=start_date,
        date__lte=end_date,
        completed=True
    )
    
    # Calculate basic stats
    total_workouts = logs.count()
    total_duration = logs.aggregate(Sum('duration'))['duration__sum'] or 0
    avg_duration = logs.aggregate(Avg('duration'))['duration__avg'] or 0
    
    # Calculate current streak
    streak = calculate_streak(user)
    
    # Calculate most used exercises
    exercise_logs = ExerciseLog.objects.filter(workout_log__in=logs)
    exercise_counts = exercise_logs.values('exercise__name').annotate(
        count=Count('exercise__name')
    ).order_by('-count')[:5]
    
    # Get day with most workouts
    day_distribution = logs.values('date__week_day').annotate(
        count=Count('id')
    ).order_by('-count')
    most_active_day = day_distribution.first() if day_distribution.exists() else None
    
    if most_active_day:
        most_active_day = get_day_name(most_active_day['date__week_day'])
    
    return {
        'period_days': days,
        'total_workouts': total_workouts,
        'total_duration': total_duration,
        'avg_duration': round(avg_duration, 1) if avg_duration else 0,
        'current_streak': streak,
        'favorite_exercises': list(exercise_counts),
        'most_active_day': most_active_day,
        'workout_frequency': round(total_workouts / days * 7, 1) if total_workouts > 0 else 0  # Weekly frequency
    }

def calculate_streak(user):
    """
    Calculate the current workout streak (consecutive days) for a user.
    
    Args:
        user: The User object
        
    Returns:
        int: Number of consecutive days with completed workouts
    """
    logs = WorkoutLog.objects.filter(
        user=user,
        completed=True
    ).order_by('-date')
    
    if not logs.exists():
        return 0
    
    streak = 1
    today = timezone.now().date()
    
    # Check if there's a workout today
    has_workout_today = logs.filter(date=today).exists()
    
    if not has_workout_today:
        # If no workout today, check if there was one yesterday to maintain streak
        yesterday = today - datetime.timedelta(days=1)
        has_workout_yesterday = logs.filter(date=yesterday).exists()
        
        if not has_workout_yesterday:
            # No workout yesterday or today = no current streak
            return 0
    
    # Start from the most recent workout date
    current_date = logs.first().date
    expected_date = current_date
    
    for log in logs:
        if log.date == expected_date or log.date == expected_date - datetime.timedelta(days=1):
            if log.date != expected_date:
                # Move to the next expected date
                expected_date = log.date
            # Valid streak day, continue counting
            if log.date != current_date:  # Avoid counting duplicate workouts on the same day
                streak += 1
                current_date = log.date
        else:
            # Streak is broken
            break
    
    return streak

# ===== Progress Tracking Functions =====

def get_exercise_progress(user, exercise_id, days=90):
    """
    Get progress data for a specific exercise over time.
    
    Args:
        user: The User object
        exercise_id: ID of the exercise to track
        days: Number of days to look back (default 90)
        
    Returns:
        list: List of dictionaries with date and performance data
    """
    end_date = timezone.now().date()
    start_date = end_date - datetime.timedelta(days=days)
    
    # Get all logs for this exercise
    logs = ExerciseLog.objects.filter(
        workout_log__user=user,
        exercise_id=exercise_id,
        workout_log__date__gte=start_date,
        workout_log__completed=True
    ).order_by('workout_log__date')
    
    progress_data = []
    
    for log in logs:
        # Parse JSON data from string fields
        try:
            reps = json.loads(log.reps_completed) if log.reps_completed else []
            weights = json.loads(log.weight_used) if log.weight_used else []
        except json.JSONDecodeError:
            # Handle case where data isn't valid JSON
            reps = [0] * log.sets_completed
            weights = [0] * log.sets_completed
        
        # Calculate volume (weight × reps)
        volume = sum(r * w for r, w in zip(reps, weights)) if reps and weights else 0
        
        # Get max weight used
        max_weight = max(weights) if weights else 0
        
        # Add data point
        progress_data.append({
            'date': log.workout_log.date,
            'sets': log.sets_completed,
            'reps': reps,
            'weights': weights,
            'volume': volume,
            'max_weight': max_weight,
            'notes': log.notes
        })
    
    return progress_data

def calculate_volume_progress(progress_data, window=3):
    """
    Calculate volume progress and trend from exercise progress data.
    
    Args:
        progress_data: List from get_exercise_progress function
        window: Window size for trend calculation (default 3)
        
    Returns:
        dict: Progress statistics
    """
    if not progress_data or len(progress_data) < 2:
        return {
            'volume_change': 0,
            'is_improving': False,
            'trend': 'neutral',
            'enough_data': False
        }
    
    # Get first and last workout volumes
    first_volume = progress_data[0]['volume']
    last_volume = progress_data[-1]['volume']
    
    # Calculate volume change
    volume_change = last_volume - first_volume
    volume_change_percent = (volume_change / first_volume * 100) if first_volume > 0 else 0
    
    # Calculate trend using window
    if len(progress_data) >= window:
        recent_volumes = [entry['volume'] for entry in progress_data[-window:]]
        is_trending_up = all(recent_volumes[i] <= recent_volumes[i+1] for i in range(len(recent_volumes)-1))
        is_trending_down = all(recent_volumes[i] >= recent_volumes[i+1] for i in range(len(recent_volumes)-1))
        
        if is_trending_up:
            trend = 'improving'
        elif is_trending_down:
            trend = 'declining'
        else:
            trend = 'fluctuating'
    else:
        trend = 'neutral'
    
    return {
        'volume_change': volume_change,
        'volume_change_percent': round(volume_change_percent, 1),
        'is_improving': volume_change > 0,
        'trend': trend,
        'enough_data': len(progress_data) >= 2
    }

# ===== Recommendation Functions =====

def suggest_workout(user):
    """
    Suggest a workout for today based on user's history and patterns.
    
    Args:
        user: The User object
        
    Returns:
        dict: Suggested workout information or None if no plans exist
    """
    # Get all user's workout plans
    plans = WorkoutPlan.objects.filter(user=user)
    
    if not plans.exists():
        return None
    
    # Get recent workout logs
    recent_logs = WorkoutLog.objects.filter(
        user=user,
        completed=True
    ).order_by('-date')[:5]
    
    # Check what was done recently to avoid repetition
    recent_day_ids = [log.workout_day_id for log in recent_logs]
    
    # Get all workout days, excluding recently completed ones if possible
    all_days = WorkoutDay.objects.filter(plan__in=plans)
    available_days = all_days.exclude(id__in=recent_day_ids) if recent_day_ids and len(all_days) > len(recent_day_ids) else all_days
    
    if not available_days.exists():
        # If all workouts were recently completed, suggest the least recently completed
        if recent_logs.exists():
            return {
                'workout_day': recent_logs.last().workout_day,
                'reason': 'All workouts completed recently. This is the least recent one.'
            }
        else:
            # If no workout logs exist, suggest the first available workout day
            return {
                'workout_day': all_days.first(),
                'reason': 'No recent workouts. Try this one to get started.'
            }
    
    # Check if there's a pattern of working out on this day of the week
    today_weekday = timezone.now().date().weekday()
    
    # Find workouts done on this day of the week
    same_weekday_logs = WorkoutLog.objects.filter(
        user=user,
        date__week_day=today_weekday + 2,  # Django uses 1-7 where 1=Sunday, so add 2 to 0-based weekday
        completed=True
    ).values('workout_day').annotate(count=Count('workout_day')).order_by('-count')
    
    if same_weekday_logs.exists():
        # Get the most frequently done workout on this day of the week
        frequent_day_id = same_weekday_logs.first()['workout_day']
        frequent_day = WorkoutDay.objects.get(id=frequent_day_id)
        
        if frequent_day_id not in recent_day_ids:
            return {
                'workout_day': frequent_day,
                'reason': f'You often do this workout on {get_day_name(today_weekday + 2)}.'
            }
    
    # Default: suggest a workout that hasn't been done recently
    return {
        'workout_day': available_days.first(),
        'reason': 'You haven\'t done this workout recently.'
    }

# ===== Helper Functions =====

def get_day_name(weekday_number):
    """
    Convert Django's weekday number to day name.
    
    Args:
        weekday_number: Django weekday number (1=Sunday, 2=Monday, etc.)
        
    Returns:
        str: Day name
    """
    days = {
        1: 'Sunday',
        2: 'Monday',
        3: 'Tuesday',
        4: 'Wednesday',
        5: 'Thursday',
        6: 'Friday',
        7: 'Saturday'
    }
    return days.get(weekday_number, 'Unknown')

def parse_reps_or_weights(data_string):
    """
    Safely parse JSON string of reps or weights from ExerciseLog.
    
    Args:
        data_string: JSON string to parse
        
    Returns:
        list: Parsed data or empty list if invalid
    """
    if not data_string:
        return []
    
    try:
        data = json.loads(data_string)
        if isinstance(data, list):
            return data
        return []
    except json.JSONDecodeError:
        return []

def format_duration(minutes):
    """
    Format duration in minutes to a human-readable string.
    
    Args:
        minutes: Duration in minutes
        
    Returns:
        str: Formatted duration string
    """
    if minutes < 60:
        return f"{minutes} min"
    
    hours = minutes // 60
    mins = minutes % 60
    
    if mins == 0:
        return f"{hours} hr"
    
    return f"{hours} hr {mins} min"

def calculate_bmi(user_profile):
    """
    Calculate BMI for a user profile.
    
    Args:
        user_profile: UserProfile object
        
    Returns:
        float: BMI value or None if data missing
    """
    if not user_profile.height or not user_profile.weight or user_profile.height <= 0:
        return None
    
    # Height in meters (convert from cm)
    height_m = user_profile.height / 100
    
    # BMI formula: weight (kg) / height^2 (m)
    bmi = user_profile.weight / (height_m * height_m)
    
    return round(bmi, 1)

def get_bmi_category(bmi):
    """
    Get the BMI category based on the BMI value.
    
    Args:
        bmi: BMI value
        
    Returns:
        str: BMI category
    """
    if bmi is None:
        return None
    
    if bmi < 18.5:
        return "Underweight"
    elif bmi < 25:
        return "Normal weight"
    elif bmi < 30:
        return "Overweight"
    else:
        return "Obese"