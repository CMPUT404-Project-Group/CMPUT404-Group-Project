from django.urls import include, path
from . import views

app_name = "api"
urlpatterns = [
    path('authors/', views.authors, name="authors"),
    path('author/<str:author_id>/', views.author, name="author"),
    path('posts/<str:post_id>', views.posts, name="posts")
]
