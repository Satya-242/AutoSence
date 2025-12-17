from django.shortcuts import redirect
from django.urls import reverse

class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # Define paths that don't require authentication
        self.allowed_paths = [
            '/login/',
            '/signup/',
            '/admin/',
        ]

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        # Skip middleware for static files
        if request.path.startswith('/static/') or request.path.startswith('/media/'):
            return None
            
        # Allow access to allowed paths
        if any(request.path.startswith(path) for path in self.allowed_paths):
            return None
            
        # Allow access if user is authenticated
        if request.user.is_authenticated:
            return None
            
        # Redirect to login page for unauthenticated users
        return redirect('login')
