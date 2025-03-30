"""
Custom template tags for Workout App
"""

from django import template
from django.utils import timezone
import json
from workout_app.workout_utils import calculate_bmi, get_bmi_category, format_duration, parse_reps_or_weights

register = template.Library()

@register.filter
def get_bmi(user_profile):
    """Calculate BMI from user profile"""
    return calculate_bmi(user_profile)

@register.filter
def bmi_category(bmi_value):
    """Get BMI category from BMI value"""
    return get_bmi_category(bmi_value)

@register.filter
def format_mins(minutes):
    """Format minutes to human-readable duration"""
    return format_duration(minutes)

@register.filter
def parse_json(json_string):
    """Parse JSON string to Python object"""
    if not json_string:
        return []
    try:
        return json.loads(json_string)
    except json.JSONDecodeError:
        return []

@register.simple_tag
def streak_class(streak_count):
    """Return CSS class based on streak count"""
    if streak_count >= 30:
        return "text-success fw-bold"
    elif streak_count >= 7:
        return "text-primary fw-bold"
    elif streak_count >= 3:
        return "text-info"
    else:
        return "text-muted"

@register.simple_tag
def workout_suggestion(user):
    """Get workout suggestion for user"""
    from workout_app.workout_utils import suggest_workout
    suggestion = suggest_workout(user)
    if suggestion:
        return suggestion
    return None

@register.filter
def days_since(date):
    """Calculate days since given date"""
    if not date:
        return None
    delta = timezone.now().date() - date
    return delta.days

@register.filter
def absolute(value):
    """Return the absolute value of a number"""
    try:
        return abs(value)
    except (ValueError, TypeError):
        return value