from django.contrib import admin
from django.contrib.auth.models import Group, User
from .models import Profile, Post
#unregister Groups

admin.site.unregister(Group)
admin.site.register(Profile)
admin.site.register(Post)

#register profile
#admin.site.register(Profile)

#merge user prfile into User
