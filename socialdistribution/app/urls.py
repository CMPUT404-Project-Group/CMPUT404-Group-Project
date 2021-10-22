from django.urls import include, path
from . import views

app_name = "app"
urlpatterns = [
    path('', views.index, name="index"),
    path('accounts/', include('django.contrib.auth.urls')),
    path('register/', views.register, name="register"),
    path('create-post/', views.create_post, name='create-post'),
    path('posts/edit-post/<str:post_id>', views.edit_post, name='edit-post'),
    path('posts/<str:post_id>', views.post, name='posts')
]
