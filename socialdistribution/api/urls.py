from django.urls import include, path
from . import views

app_name = "api"
urlpatterns = [
    path('authors/', views.authors, name="authors"),
    path('author/<str:author_id>/', views.author, name="author"),
    path('author/<str:author_id>/inbox', views.Inbox.as_view(), name='inbox'),
    path('posts/<str:post_id>', views.posts, name="posts")
]
