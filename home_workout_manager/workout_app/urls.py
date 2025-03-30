from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView
from django.views.decorators.http import require_http_methods

urlpatterns = [
    # Authentication URLs
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='workout_app/login.html'), name='login'),
    
    # Updated logout view to handle both GET and POST methods
    path('logout/', auth_views.LogoutView.as_view(
        next_page='login',  # Redirect to login page after logout
        template_name='workout_app/logout.html'  # Use the custom template
    ), name='logout'),
    
    # Redirect from Django's default login URL to our custom login URL
    path('accounts/login/', RedirectView.as_view(pattern_name='login'), name='default_login'),
    
    # Main application URLs
    path('', views.dashboard, name='dashboard'),
    
    # Workout Plans
    path('workout-plans/', views.workout_plans, name='workout_plans'),
    path('workout-plans/<int:pk>/', views.workout_plan_detail, name='workout_plan_detail'),
    path('workout-plans/<int:pk>/delete/', views.delete_workout_plan, name='delete_workout_plan'),
    
    # Workout Days
    path('workout-days/<int:pk>/', views.workout_day_detail, name='workout_day_detail'),
    
    # Workout Exercises
    path('workout-exercises/<int:pk>/delete/', views.delete_workout_exercise, name='delete_workout_exercise'),
    path('update-exercise-order/', views.update_exercise_order, name='update_exercise_order'),
    
    # Exercise Library
    path('exercises/', views.exercise_library, name='exercise_library'),
    path('exercises/<int:pk>/', views.exercise_detail, name='exercise_detail'),
    
    # Workout Sessions
    path('workout/', views.workout, name='workout'),
    path('start-workout/', views.start_workout, name='start_workout'),
    path('start-workout/<int:day_pk>/', views.start_workout, name='start_workout_day'),
    path('perform-workout/<int:log_pk>/', views.perform_workout, name='perform_workout'),
    
    # Progress Tracking
    path('progress/', views.progress, name='progress'),
    
    # User Settings
    path('settings/', views.settings, name='settings'),
    path('stats/', views.advanced_stats, name='advanced_stats'),
]