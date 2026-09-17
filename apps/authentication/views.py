from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect

def login_view(request):
    if request.method == 'POST':
        username_input = request.POST.get('username')
        password_input = request.POST.get('password')
        
        user = authenticate(request, username=username_input, password=password_input)
        
        if user is not None:
            login(request, user)
            
            if user.groups.filter(name='Owner').exists():
                return redirect('/')
            else:
                return redirect('/')
        else:
            return render(request, 'authentication/login.html', {'error': 'اسم المستخدم أو كلمة المرور غير صحيحة'})
            
    return render(request, 'authentication/login.html')

# Create your views here.
