from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('profile_list/', views.profile_list, name= 'profile_list'),
    path('profile/<int:pk>', views.profile, name='profile'),
    path('profile/followers/<int:pk>', views.followers, name='followers'),
    path('profile/follows/<int:pk>', views.follows, name='follows'),
    path('login', views.login_view, name= 'login'),
    path('logout', views.logout_view, name='logout'),
    path('register', views.register_user, name= 'register'),
    path('update-user', views.update_user, name='update_user'),
    path('post-likes/<int:pk>', views.post_like, name= 'post-like'),
    path('share-post/<int:pk>', views.share_post, name= 'share-post'),
    path('follow/<int:pk>', views.follow, name='follow'),
    path('unfollow/<int:pk>', views.unfollow, name='unfollow'),
    path('delete-post<int:pk>', views.delete_post, name='delete-post'),
    path('edit-post/<int:pk>', views.edit_post, name='edit-post'),
    path('search', views.search, name='search'),
    path('search_user', views.search_user, name='search_user'),

    path('create-post', views.create_post, name='create-post'),

    # email settings
    path('activate/<uidb64>/<token>', views.activate, name='activate'),

]
