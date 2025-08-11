from django.shortcuts import render,redirect, HttpResponse
from .forms import RegistrationForm
from .models import Account
from django.contrib import messages,auth
from django.contrib.auth.decorators import login_required
# Create your views here.


#Verification email
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode,urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage

def register(request):

    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name      = form.cleaned_data['first_name']
            last_name       = form.cleaned_data['last_name']
            phone_number    = form.cleaned_data['phone_number']
            email           = form.cleaned_data['email']
            password        = form.cleaned_data['password']
            username        = email.split("@")[0]
            user = Account.objects.create_user(first_name = first_name, last_name = last_name,  email = email, username = username, password = password)
            user.phone_number = phone_number
            user.save()

            # User Activation Mail Send to activate account
            current_site = get_current_site(request)
            mail_subject = 'Activate your account'
            message = render_to_string('accounts/account_verification_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            send_email = EmailMessage(mail_subject, message, to=[user.email])
            send_email.send()
            # messages.success(request, 'Thank you for registring with us. we have sent you a verification email to your email address. please verify it.')
            return redirect('/accounts/login/?command=verification&email='+email)

    else:

        form = RegistrationForm()
    context = {
        'form':form,
    }
    return render(request, 'accounts/register.html',context)


def login(request):
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']

        print(email)
        print("pass", password)

        user = auth.authenticate(email=email, password=password)

        print("user is  ",user)

        if user is not None:
            auth.login(request, user)
            print("login done ")
            messages.success(request,"You are now logged in")
            return redirect("dashbord")
        else:
            messages.error(request, "Invaild login crediantial ")
            return redirect("login")

    return render(request, 'accounts/login.html')

@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    messages.error(request, "You are loged out")
    return redirect("login")



def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Congratulations! Your account is activated')
        return redirect('login')
    else:
        messages.error(request, 'invaild avtivation link')
        return redirect('register')
    


def dashbord(request):

    return render(request, 'accounts/dashbord.html')


def forgotPassword(request):
    if request.method == "POST":
        email = request.POST['email']

        if Account.objects.filter(email = email).exists:
            user = Account.objects.get(email__exact = email)

            # User forgotpassword Mail Send to rest password
            current_site = get_current_site(request)
            mail_subject = 'Rest your Password'
            message = render_to_string('accounts/reset_password_account.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            send_email = EmailMessage(mail_subject, message, to=[user.email])
            send_email.send()
            messages.success(request, 'Password reset email has been sent to your email address.')
            return redirect('login')

        else:
            message.error(request, 'Account doesnot exit ')
            return redirect('forgotPassword')
    return render(request, 'accounts/forgotPassword.html')



def restPassword_validation(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request, 'please reset your password')
        return redirect('reset_password')
    else:
        messages.error(request, 'This link has been expired')
        return redirect('login')


def restPassword(request):

    if request.method == "POST":
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request, 'password reset successful')
            return redirect('login')
        else:
            messages.error(request,'Password do not match!')
            return redirect('reset_password')
    else:
        return render(request, 'accounts/resetpassword.html')
