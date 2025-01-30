from django.shortcuts import render, get_object_or_404
from .models import Profile

def index(request):
    # Check if the user is authenticated
    if request.user.is_authenticated:
        # Get the profile or return a 404 if not found
        profile = get_object_or_404(Profile, user=request.user)
    else:
        # Handle unauthenticated users (e.g., use a default profile or None)
        profile = None
    
    # Pass the profile to the template
    return render(request, 'core/index.html', {'profile': profile})


def custom_404_view(request, exception):
    return render(request, 'core/404.html', status=404)

def custom_500_view(request):
    return render(request, 'core/500.html', status=500)