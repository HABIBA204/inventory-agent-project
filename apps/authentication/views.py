from django.contrib.auth import authenticate, login, logout
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


def logout_view(request):
    # بيمسح جلسة اليوزر الحالية (الكوكي بتاعة تسجيل الدخول)
    # وبعدها أي محاولة دخول على الموقع هتتحول لصفحة اللوجين تاني
    logout(request)
    return redirect('login')

# Create your views here.