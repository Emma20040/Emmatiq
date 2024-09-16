from django.contrib import admin
from django.contrib.auth.models import Group, User
from .models import Profile, Post
#unregister Groups

admin.site.unregister(Group)

#extend user model
class ProfileInline(admin.StackedInline):
    model= Profile

class UserAdmin(admin.ModelAdmin):
    model= User
    # displays only usernam in the admin page
    fields= ['username']
    inlines = [ProfileInline]

# unregister intial user
admin.site.unregister(User)

#reregister user again

admin.site.register(User, UserAdmin)

admin.site.register(Post)

#register profile
#admin.site.register(Profile)

#merge user prfile into User
