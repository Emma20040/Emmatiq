from typing import Any
from django import forms
from .models import Post
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordResetForm



class ProfilePicForm(forms.ModelForm):
    profile_pic =forms.ImageField(label ='Profile Picture', required=False)

    profile_bio= forms.CharField(label="profile_bio", required=False,
                                 widget= forms.Textarea(attrs={'class':'form-control', 'placeholder':'Profile bio'}))
    twitter_link=forms.CharField(label="Twitter link", required= False,
                                 widget= forms.TextInput(attrs={'class':'form-control', 'placeholder':'Twitter link'}))
    github_link= forms.CharField(label="Github link", required=False,
                                 widget= forms.TextInput(attrs={'class':'form-control', 'placeholder':'Github Link'}))
    linkedln_link= forms.CharField(label="Linkedln link", required=False,
                                 widget= forms.TextInput(attrs={'class':'form-control', 'placeholder':'Linkedln Link'}))
    portfolio_link= forms.CharField(label="Portfolio link", required= False,
                                 widget= forms.TextInput(attrs={'class':'form-control', 'placeholder':'Portfolio Link'}))

    class Meta:
        model = Profile
        fields =('profile_pic', 'profile_bio', 'twitter_link', 'github_link', 'linkedln_link', 'portfolio_link',)


class PostForm(forms.ModelForm):
    body = forms.CharField(required=False, 
                           widget=forms.widgets.Textarea(
                               attrs={"placeholder": "type your post here",
                                      "class": "form-control",}
                           ),
                           label=""
                           )
    image= forms.ImageField(required=False,
                           widget=forms.widgets.FileInput(
                               attrs={"placeholder": "upload your image here",
                                      "class": "form-control",}
                           ),
                           label=""
                           )

    class Meta:
        model = Post
        fields= ['body', 'image']
        exclude =("user", "likes",)


class SignupForm(UserCreationForm):
    email = forms.EmailField(label='',
                             widget= forms.TextInput(attrs={'class':'form-control', 'placeholder':'Email adress'}))
    first_name= forms.CharField(label='', required=False, max_length=100, widget= forms.TextInput(attrs={'class':'form-control', 'placeholder':'First name'}))
    last_name= forms.CharField(label='', required=False, max_length=100, widget= forms.TextInput(attrs={'class':'form-control', 'placeholder':'last name'}))

    class Meta:
        model = User
        fields =('username', 'first_name', 'last_name', 'email','password1', 'password',)

    def __init__(self, *args, **kwargs):
        super(SignupForm, self).__init__(*args, **kwargs)

        self.fields['username'].widget.attrs['class'] = 'form-control'
        self.fields['username'].widget.attrs['placeholder'] = 'User Name'
        self.fields['username'].label = ''
        self.fields['username'].help_text = '<span class="form-text text-muted"><small>Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.</small></span>'

        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password1'].widget.attrs['placeholder'] = 'Password'
        self.fields['password1'].label = ''
        self.fields['password1'].help_text = '<ul class="form-text text-muted small"><li>Your password can\'t be too similar to your other personal information.</li><li>Your password must contain at least 8 characters.</li><li>Your password can\'t be a commonly used password.</li><li>Your password can\'t be entirely numeric.</li></ul>'

        self.fields['password2'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['placeholder'] = 'Confirm Password'
        self.fields['password2'].label = ''
        self.fields['password2'].help_text = '<span class="form-text text-muted"><small>Enter the same password as before, for verification.</small></span>'


class SetPasswordForm(SetPasswordForm):
    class Meta:
        model = get_user_model()
        fields = ['new_password1', 'new_password2']


class PasswordResetForm(PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super(PasswordResetForm, self).__init__(*args, **kwargs)