from django.shortcuts import render, redirect, get_object_or_404, redirect
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.tokens import default_token_generator
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods, require_GET, require_POST
from django.core.mail import EmailMultiAlternatives
from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings
from django.template import loader
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.decorators import login_required
from .forms import LoginForm, SignupForm, ForgotPasswordForm, ResetPasswordForm
from .models import CustomUser

# Create your views here.

def index(request):
    context = {}
    return render(request, 'base/index.html', context)

@require_http_methods(['GET', 'POST'])
def login(request):
    if request.user.is_authenticated():
        return redirect('home')
    if request.method == 'GET':
        f = LoginForm()
    elif request.method == 'POST':
        f = LoginForm(request.POST)
        if f.is_valid():
            user = f.get_user()
            auth_login(request, user)
            return redirect('dashboard')
    return render(request, 'authentication/login.html', { 'form': f })

@require_GET
def logout(request):
    auth_logout(request)
    return redirect('login')

@require_GET
@login_required
def dashboard(request):
    return render(request, 'base/dashboard.html')


@require_http_methods(['GET', 'POST'])
def signup(request):
    if request.user.is_authenticated():
        return redirect('home')
    if request.method == 'GET':
        f = SignupForm()
    else:
        f = SignupForm(request.POST)
        if f.is_valid():
            user = f.save()
            # Send verification email as well
            email_body_context = {
                'username': user.username,
                'token': urlsafe_base64_encode(force_bytes(user.username)), # As encode func takes bytes not string
                'uid': user.id,
                'protocol': 'https' if settings.USE_HTTPS else 'http',
                'domain': get_current_site(request).domain,
            }
            body = loader.render_to_string('authentication/signup_email_body_text.html', email_body_context)
            subject = 'Welcome to PosterInfinity'
            email_message = EmailMultiAlternatives(subject, body, settings.DEFAULT_FROM_EMAIL, [user.email])
            email_message.send()
            return render(request, 'authentication/signup_email_sent.html', { 'email': user.email })
    return render(request, 'authentication/signup.html', { 'form': f })

@require_GET
def activate(request, uid = None, token = None):
    if request.user.is_authenticated():
        return redirect('home')
    '''
    try:
        user = CustomUser.objects.get(id = uid)
    except CustomUser.DoesNotExist:
        raise Http404('Invalid User')
    '''
    user = get_object_or_404(CustomUser, id = uid)
    username_from_token = force_text(urlsafe_base64_decode(token))
    if user.is_active:
        return redirect('login')

    if user.username == username_from_token:
        user.is_active = True
        user.save()
        return render(request, 'authentication/activation_success.html')
    else:
        return render(request, 'authentication/activation_failure.html')

@require_http_methods(['GET', 'POST'])
def forgot_password(request):
    if request.user.is_authenticated():
        return redirect('index')
    if request.method == 'GET':
        f = ForgotPasswordForm()
    if request.method == 'POST':
        f = ForgotPasswordForm(request.POST)
        if f.is_valid():
            user = CustomUser.objects.get(email = f.cleaned_data['email'])
            email_body_context = {
                'username': user.username,
                'token': default_token_generator.make_token(user),
                'uid': user.id,
                'protocol': 'https' if settings.USE_HTTPS else 'http',
                'domain': get_current_site(request).domain,
            }
            body = loader.render_to_string('authentication/forgot_password_email_body_text.html', email_body_context)
            subject = 'Please reset your password'
            email_message = EmailMultiAlternatives(subject, body, settings.DEFAULT_FROM_EMAIL, [user.email])
            email_message.send()
            context = { 'email': user.email }
            return render(request, 'authentication/forgot_password_email_sent.html', context)

    context = { 'form': f }
    return render(request, 'authentication/forgot_password.html', context)

@require_http_methods(['GET', 'POST'])
def reset_password(request, uid = None, token = None):
    if request.user.is_authenticated():
        return redirect('home')
    try:
        user = CustomUser.objects.get(id = uid)
    except CustomUser.DoesNotExist:
        user = None
    if not user or not default_token_generator.check_token(user, token):
        context = { 'validlink': False }
        return render(request, 'authentication/reset_password.html', context)

    if request.method == 'GET':
        f = ResetPasswordForm()
    else:
        f = ResetPasswordForm(request.POST)
        if f.is_valid():
            user.set_password(f.cleaned_data['password1'])
            user.save()
            return redirect('login')

    context = { 'validlink': True, 'form': f }
    return render(request, 'authentication/reset_password.html', context)
