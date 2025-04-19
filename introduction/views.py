from django.shortcuts import render

def introduction_view(request):
    return render(request, 'introduction/introduction.html')

def home_view(request):
    return render(request, 'introduction/home.html')


