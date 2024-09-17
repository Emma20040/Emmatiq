from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Profile, Post
from django.contrib.auth import authenticate
from .forms import PostForm, SignupForm, ProfilePicForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django import forms 
from django.contrib.auth.models import User
from django.http import HttpResponse


def home(request):
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
        posts= Post.objects.all().order_by("-created_at")
        context= {'posts':posts, 'form':form} 
        return render(request, 'base/home.html', context)
    else:
        posts= Post.objects.all().order_by("-created_at")
        context= {'posts':posts}   
        return render(request, 'base/home.html', context)
# Create your views here.


def profile_list(request):
    if request.user.is_authenticated:
        profiles = Profile.objects.exclude(user= request.user)
        context= {"profiles":profiles }
        return render(request, 'base/profile_list.html', context)
    
    else:
        messages.success(request,('Only login users can view this page'))
        return redirect('home')
    

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


def register_user(request):
    form = SignupForm()
    if request.method =="POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()
            username= form.cleaned_data['username']
            password= form.cleaned_data['password1']
            email = form.cleaned_data['email']
            first_name= form.cleaned_data['first_name']
            laast_name= form.cleaned_data['last_name']

            user= authenticate(username= username, password=password)
            login(request, user)
            messages.success(request, ("You have successfully singup, welcome to EMMATIQ"))
            return redirect('home')
    
    context={'form':form}
    return render(request, 'base/register.html', context)


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
            messages.success(request, ("you can't delete this post becuase it is not your post"))
            return redirect('home')
    else:
        messages.success(request, ("Only owners of the post can delete"))
        return redirect('home')
    

def search(request):
	if request.method == "POST":
		# Grab the form field input
		search = request.POST['search']
		# Search the database
		searched = Post.objects.filter(body__contains = search)

		return render(request, 'base/search.html', {'search':search, 'searched':searched})
	else:
		return render(request, 'base/search.html', {}) 
    


def search_user(request):
	if request.method == "POST":
		# Grab the form field input
		search = request.POST['search']
		# Search the database
		searched = User.objects.filter(username__contains = search)

		return render(request, 'base/search_user.html', {'search':search, 'searched':searched})
	else:
		return render(request, 'base/search_user.html', {}) 
    


