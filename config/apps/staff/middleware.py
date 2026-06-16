# apps/staff/middleware.py
from django.shortcuts import redirect

class StaffMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/staff/'):
            if not request.user.is_authenticated or not request.user.is_staff:
                return redirect('login')
        return self.get_response(request)