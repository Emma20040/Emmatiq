from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Profile, Post
from django.contrib.auth import authenticate
from .forms import PostForm, SignupForm, ProfilePicForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django import forms 
from django.contrib.auth.models import User
from django.db.models import Count
# email settings
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage
from django.contrib.auth import get_user_model
from .tokens import account_activation_token
# reset password
from .forms import SetPasswordForm, PasswordResetForm
from django.db.models.query_utils import Q


def home(request):
    posts=Post.objects.all().order_by("-created_at")
    trending_post = Post.objects.all().annotate(num_likes=Count('likes')).order_by('-num_likes')[:5] 
    context={"posts":posts, "trending_post":trending_post}
    return render(request, 'base/home.html', context)


# view that users to create a post
def create_post(request):
    if request.user.is_authenticated:
        form= PostForm()
        if request.method== "POST":
            form= PostForm(request.POST, request.FILES)
            if form.is_valid():
                post= form.save(commit=False)
                post.user= request.user
                post.save()
                messages.success(request,('Your post was successfully created'))
                return redirect('home')
        # posts= Post.objects.all().order_by("-created_at")
        context= {'form':form} 
        return render(request, 'base/create_post.html', context)
    else:
        messages.success(request, ('You must be login to post'))
        # posts= Post.objects.all().order_by("-created_at")
        # context= {'posts':posts}   
        return redirect('login')
# Create your views here.


# list of all user in the system
def profile_list(request):
    if request.user.is_authenticated:
        profiles = Profile.objects.exclude(user= request.user)
        context= {"profiles":profiles }
        return render(request, 'base/profile_list.html', context)
    
    else:
        messages.success(request,('Only login users can view this page'))
        return redirect('home')
    

# user profile
def profile(request, pk):
    if request.user.is_authenticated:
        profile= Profile.objects.get(user_id=pk)
        posts= Post.objects.filter(user_id= pk).order_by("-created_at")
        #logic to follow and unfollow profiles
        if request.method=="POST":
            #get the current user 
            current_user_profile= request.user.profile
            #get form data
            action= request.POST['follow']
            # decide to follow or unfollow
            if action == 'unfollow':
                current_user_profile.follows.remove(profile)
            elif action== 'follow':
                current_user_profile.follows.add(profile)
            current_user_profile.save()
        context= {'profile':profile, 'posts':posts}
        return render(request, 'base/profile.html', context)
    
    else:
        messages.success(request, ("only login users have profile"))
        return redirect('home')


def login_view(request):
    if request.method== "POST":
        username= request.POST['username']
        password= request.POST['password']
        user= authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, ('you have successfully login'))
            return redirect('home')
        else:
            messages.success(request, ("an error occured during login"))
            return redirect('login')
        
    else:
        return render(request, 'base/login.html', {})


def logout_view(request):
    logout(request)
    messages.success(request, ("You have been logout"))
    return redirect('home')


# email views
def activate(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()

        messages.success(request, 'Thank you for your email confirmation. Now you can login your account.')
        return redirect('login')
    else:
        messages.error(request, 'Activation link is invalid!')
    
    return redirect('home')


def activateEmail(request, user, to_email):
    mail_subject = 'Activate your user account.'
    message = render_to_string('base/template_activate_account.html', {
        'user': user.username,
        'domain': get_current_site(request).domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
        'protocol': 'https' if request.is_secure() else 'http'
    })
    email = EmailMessage(mail_subject, message, to=[to_email])
    if email.send():
        messages.success(request, f'Dear <b>{user}</b>, please go to you email <b>{to_email}</b> inbox and click on \
            received activation link to confirm and complete the registration. <b>Note:</b> Check your spam folder.')
    else:
        messages.error(request, f'Problem sending confirmation email to {to_email}, check if you typed it correctly.')

# def activateEmail(request, user, to_email):
#     messages.success(request, f'Dear <b>{user}</b>, please go to you email <b>{to_email}</b> inbox and click on \
#         received activation link to confirm and complete the registration. <b>Note:</b> Check your spam folder.')


# new registeration view with email 
def register_user(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            # "user.is_active=False", meaning a user cannot log in until the email is verified.
            user.is_active = False
            user.save()
            activateEmail(request, user, form.cleaned_data.get('email'))
            return redirect('home')

        else:
            for error in list(form.errors.values()):
                messages.error(request, error)

    else:
        form = SignupForm()
    
    context={"form":form}
    return render(request, "base/register.html", context)

# old registeration views without email
# def register_user(request):
#     form = SignupForm()
#     if request.method =="POST":
#     form = SignupForm(request.POST)
#     if form.is_valid():
#         form.save()
#         username= form.cleaned_data['username']
#         password= form.cleaned_data['password1']
#         email = form.cleaned_data['email']
#         first_name= form.cleaned_data['first_name']
#         laast_name= form.cleaned_data['last_name']

#         user= authenticate(username= username, password=password)
#         login(request, user)
#         messages.success(request, ("You have successfully singup, welcome to EMMATIQ"))
#         return redirect('home')

#     context={'form':form}
#     return render(request, 'base/register.html', context)


# view to update user profile
def update_user(request):
    if request.user.is_authenticated:
        current_user= User.objects.get(id=request.user.id)
        profile_user= Profile.objects.get(user__id= request.user.id)
        user_form= SignupForm(request.POST or None, request.FILES or None, instance= current_user)
        profile_form =ProfilePicForm(request.POST or None, request.FILES or None, instance=profile_user)
        if user_form.is_valid() and profile_form.is_valid():
                user_form.save()
                profile_form.save()
                login(request, current_user)
                messages.success(request, ("You must be logged in to view before you can update your profile"))
                return redirect('home')

        context= {'user_form':user_form, 'profile_form':profile_form}
        return render(request, 'base/update_user.html', context)
    
    else:
        messages.success(request, ("You must be logged in to view before you can update your profile"))
        return redirect('home')


# allow user to follow to profile
def follow(request, pk):
    if request.user.is_authenticated:
        #get the user profile to follow
        profile= Profile.objects.get(user_id=pk)
        #follow the user
        request.user.profile.follows.add(profile)
        request.user.profile.save()
        messages.success(request, (f"You have followed {profile.user.username}"))
        return redirect(request.META.get("HTTP_REFERER"))
    else:
        messages.success(request, ("You must be logged in to follow "))
        return redirect('home')


# allows user to unfollow profiles
def unfollow(request, pk):
    if request.user.is_authenticated:
        #get the user profile to unfollow
        profile= Profile.objects.get(user_id=pk)
        #unfollow the user
        request.user.profile.follows.remove(profile)
        request.user.profile.save()
        messages.success(request, (f"You have unfollowed {profile.user.username}"))
        return redirect(request.META.get("HTTP_REFERER"))
    else:
        messages.success(request, ("You must be logged in to unfollow "))
        return redirect('home')


# shows the list of every profile following you
def followers(request, pk):
    if request.user.is_authenticated:
        if request.user.id== pk:
            profiles = Profile.objects.get(user_id= pk)
            context= {"profiles":profiles }
            return render(request, 'base/followers.html', context)
        else:
            messages.success(request,('Only account owner can view their followers'))
            return redirect('home')
    
    else:
        messages.success(request,('Only login users can view this page'))
        return redirect('home')


# list of everry profile that you are following 
def follows(request, pk):
    if request.user.is_authenticated:
        if request.user.id== pk:
            profiles = Profile.objects.get(user_id= pk)
            context= {"profiles":profiles }
            return render(request, 'base/follows.html', context)
        else:
            messages.success(request,('Only account owner can view people who follow them'))
            return redirect('home')
    
    else:
        messages.success(request,('Only login users can view this page'))
        return redirect('home')


# allow users to like a post
def post_like(request, pk):
    if request.user.is_authenticated:
        post= get_object_or_404(Post, id=pk)
        if post.likes.filter(id= request.user.id):
            post.likes.remove(request.user)
        else:
            post.likes.add(request.user)
        
        return redirect(request.META.get("HTTP_REFERER"))
    
    else:
        messages.success(request, ("You Must Be Logged In To View That Page..."))
        return redirect('home')
    

     # allows user to share a post 
def share_post(request, pk):
    post= get_object_or_404(Post, id=pk)
    if post:
        context={'post':post}
        return render(request, 'base/share_post.html', context)
    
    else:
        messages.success(request, ("this post does exist"))
        return redirect('home')
    

def delete_post(request, pk):
    if request.user.is_authenticated:
        post= get_object_or_404(Post, id=pk)
         # checks if you are the owner of the post
        if request.user.username == post.user.username:
            post.delete()
            messages.success(request, ("Your post has been deleted"))
            return redirect(request.META.get("HTTP_REFERER"))
        else:
            messages.success(request, ("you can't delete this post becuase it is not your post"))
            return redirect('home')
    else:
        messages.success(request, ("Only owners of the post can delete"))
        return redirect(request.META.get("HTTP_REFERER"))
    

def edit_post(request, pk):
    if request.user.is_authenticated:
        post= get_object_or_404(Post, id=pk)
        # checks if you are the owner of the post
        if request.user.username == post.user.username:
            form= PostForm(request.POST or None, instance=post)
            if request.method== "POST":
                if form.is_valid():
                    post= form.save(commit=False)
                    post.user= request.user
                    post.save()
                    messages.success(request,('Your post has been updated'))
                    return redirect(request.META.get("HTTP_REFERER"))
            else:
                context= {'form':form, 'post':post}
                return render(request, 'base/edit_post.html', context)
                
            
        else:
            messages.success(request, ("you can't edit this post becuase it is not your post"))
            return redirect('home')
    else:
        messages.success(request, ("Only owners of the post are allowed to edit"))
        return redirect('home')
    

# view to allows user to search a post in the database
def search(request):
	if request.method == "POST":
		# Grab the form field input
		search = request.POST['search']
		# Search the database
		searched = Post.objects.filter(body__contains = search)

		return render(request, 'base/search.html', {'search':search, 'searched':searched})
	else:
		return render(request, 'base/search.html', {}) 
    

# allows user to search another profile
def search_user(request):
	if request.method == "POST":
		# Grab the form field input
		search = request.POST['search']
		# Search the database
		searched = User.objects.filter(username__contains = search)
        
		return render(request, 'base/search_user.html', {'search':search, 'searched':searched})
	else:
		return render(request, 'base/search_user.html', {}) 
    


# reset password view

def password_change(request):
    user = request.user
    if request.method == 'POST':
        form = SetPasswordForm(user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Your password has been successfully changed")
            return redirect('login')
        else:
            for error in list(form.errors.values()):
                messages.error(request, error)

    form = SetPasswordForm(user)
    context ={'form': form}
    return render(request, 'base/confirm_password_reset.html', context)




def password_reset_request(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            user_email = form.cleaned_data['email']
            associated_user = get_user_model().objects.filter(Q(email=user_email)).first()
            if associated_user:
                subject = "Password Reset request"
                message = render_to_string("base/password_reset_template.html", {
                    'user': associated_user,
                    'domain': get_current_site(request).domain,
                    'uid': urlsafe_base64_encode(force_bytes(associated_user.pk)),
                    'token': account_activation_token.make_token(associated_user),
                    "protocol": 'https' if request.is_secure() else 'http'
                })
                email = EmailMessage(subject, message, to=[associated_user.email])
                if email.send():
                    messages.success(request,
                        """
                        Password reset sent
                        
                            We've emailed you instructions for setting your password, if an account exists with the email you entered. 
                            You should receive them shortly. If you don't receive an email, please make sure you've entered the address 
                            you registered with, and check your spam folder.
                        
                        """
                    )
                else:
                    messages.error(request, "Problem sending reset password email, <b>SERVER PROBLEM</b>")

            return redirect('home')

        for key, error in list(form.errors.items()):
            if key == 'captcha' and error[0] == 'This field is required.':
                messages.error(request, "You must pass the reCAPTCHA test")
                continue

    form = PasswordResetForm()
    context= {"form": form}
    return render( request, "base/password_reset.html", context)




def passwordResetConfirm(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except:
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        if request.method == 'POST':
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Your password has been set. You may go ahead and <b>log in </b> now.")
                return redirect('home')
            else:
                for error in list(form.errors.values()):
                    messages.error(request, error)

        form = SetPasswordForm(user)
        context= {'form': form}
        return render(request, 'base/confirm_password_reset.html', context)
    else:
        messages.error(request, "Link is expired")

    messages.error(request, 'Something went wrong, redirecting back to Homepage')
    return redirect("home")