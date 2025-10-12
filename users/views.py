from http import cookies
from http.client import responses
from django.views import generic
from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm, ResetPasswordForm
from django.core.mail import send_mail
from .models import ForgetPassMailVerify#, FpoEmailVerify
from .models import CustomUser,UserEmailVerify,UserNumberVerify
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse_lazy
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.utils.crypto import get_random_string
from django.contrib.auth.hashers import check_password
from django.core.mail import EmailMessage
from django.contrib.sites.shortcuts import get_current_site
import urllib.request
import urllib.parse
from .email import verification_mail

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse_lazy('web:index'))

def loginPage(request):
    if request.method == 'POST':
        email = request.POST.get('email', None)
        print(email)
        password = request.POST.get('password', None)
        print(password)
        if email is not None and password is not None:
            user = authenticate(request, email=email, password=password)
            print('user:',user)
            if user is not None:
                login(request, user)
                print('login sus')
                if request.user.is_superuser:
                    return HttpResponseRedirect(reverse_lazy('customadmin:home'))
                else:
                    return HttpResponseRedirect(reverse_lazy('employe:home'))
            else:
                msg='Username and password is Invalid'

            messages.error(request, msg)
    return render(request, 'registration/login.html', {'user': request.user})

def starter_view(request):
    return render(request, 'home.html', {'user': request.user})

