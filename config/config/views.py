from django.shortcuts import render

def handler_ratelimit(request, exception):
    return render(request, '429.html', status=429)