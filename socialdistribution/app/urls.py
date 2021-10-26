from django.urls import include, path
from . import views

app_name = "app"
urlpatterns = [
    path('', views.index, name="index"),
    path('accounts/', include('django.contrib.auth.urls')),
    path('register/', views.register, name="register"),
    path('create-post/', views.create_post, name='create-post'),
    path('posts/<str:post_id>/create-comment', views.create_comment, name='create-comment'),
    path('posts/edit-post/<str:post_id>', views.edit_post, name='edit-post'),
    path('posts/<str:post_id>', views.post, name='posts'),
    path('profile/', views.view_profile, name='view-profile'),
    path('profile/manage/', views.manage_profile, name='manage-profile'),
    path('profile/<str:other_user_id>', views.view_other_user, name='view-other-user'),

    path('follow/<str:other_user_id>', views.follow, name='action-follow'),
    path('unfollow/<str:other_user_id>', views.unfollow, name='action-unfollow'),



]
