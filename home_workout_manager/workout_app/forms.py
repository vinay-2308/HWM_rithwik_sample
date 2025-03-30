from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import WorkoutPlan, WorkoutDay, WorkoutExercise, Exercise, UserProfile, WorkoutLog, ExerciseLog

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']

# Add this new class for updating user information
class UserUpdateForm(forms.ModelForm):
    """Form for updating user information without changing password"""
    email = forms.EmailField()
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        
    def clean_username(self):
        """Validate username uniqueness"""
        username = self.cleaned_data.get('username')
        # If username hasn't changed, no need to check
        if username == self.instance.username:
            return username
            
        # Check if username is taken by another user
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError(f'The username "{username}" is already taken.')
        
        return username

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['height', 'weight', 'fitness_goal', 'profile_picture', 'preferred_theme']
        widgets = {
            'height': forms.NumberInput(attrs={'placeholder': 'Height in cm'}),
            'weight': forms.NumberInput(attrs={'placeholder': 'Weight in kg'}),
            'fitness_goal': forms.TextInput(attrs={'placeholder': 'e.g., Lose weight, Gain muscle, etc.'}),
        }

# Rename this to avoid conflicts
class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['height', 'weight', 'fitness_goal', 'profile_picture', 'preferred_theme']
        widgets = {
            'fitness_goal': forms.Textarea(attrs={'rows': 3}),
        }

class ExerciseForm(forms.ModelForm):
    class Meta:
        model = Exercise
        fields = ['name', 'description', 'video_url', 'image']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class WorkoutPlanForm(forms.ModelForm):
    class Meta:
        model = WorkoutPlan
        fields = ['name', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class WorkoutDayForm(forms.ModelForm):
    class Meta:
        model = WorkoutDay
        fields = ['day_name']

class WorkoutExerciseForm(forms.ModelForm):
    class Meta:
        model = WorkoutExercise
        fields = ['exercise', 'sets', 'reps', 'rest_time', 'order']
        widgets = {
            'order': forms.HiddenInput(),
        }

class ExerciseLogForm(forms.ModelForm):
    class Meta:
        model = ExerciseLog
        fields = ['sets_completed', 'reps_completed', 'weight_used', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 2}),
        }