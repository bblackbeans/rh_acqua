from django.shortcuts import render

def home(request):
    # Simple home page view
    # Can be expanded later to show featured vacancies or other info
    return render(request, "core/home.html")

