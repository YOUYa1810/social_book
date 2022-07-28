from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Profile


@login_required(login_url='signin')
def index(request):
    return render(request, 'index.html')


@login_required(login_url='signin')
def settings(request):
    return render(request, 'setting.html')

def signup(request):
    
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']
        
        if password == password2:
            if User.objects.filter(email=email).exists():
                messages.info(request, 'Email is taken')
                return redirect('signup')
            if User.objects.filter(username=username).exists():
                messages.info(request, 'Username is taken')
                return redirect('signup')
            
            user = User.objects.create_user(username=username, email=email, password=password)
            user.save()
            
            # log user in and redirect to setting page
            
            # create a profile object for the new user
            user_model = User.objects.get(username=username)
            new_profile = Profile.objects.create(user= user_model,id_user=user_model.id)
            new_profile.save()
            return redirect('singin')
        else:
            messages.info(request, 'Password are not matching')
            return redirect('signup')
    
    else:
        return render(request, 'signup.html')
   
    
def signin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect('/')
        else:
            messages.error(request, 'Credentials invalid')
            return redirect('signin')
    else:
        return render(request, 'signin.html')
    
    
@login_required(login_url='signin')
def logout(request):
    auth.logout(request)
    return redirect('signin')