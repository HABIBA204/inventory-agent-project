from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect

def login_view(request):
    error=None
    if request.method == 'POST':
        username_input = request.POST.get('username')
        password_input = request.POST.get('password')
        
        user = authenticate(request, username=username_input, password=password_input)
        
        if user is not None:
           login(request, user)
           return redirect('dashboard')
    else:
         return render(request, 'authentication/login.html', {'error': 'Username or password is Wroung'})
        

# Create your views here.
