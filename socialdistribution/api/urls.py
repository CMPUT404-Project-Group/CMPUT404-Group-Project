from django.urls import path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from . import views

schema_view = get_schema_view(
    openapi.Info(
        title="SocialDistribution API Documentation - Team 10",
        default_version='v1',
        description="API Documentation for Team 10's Social Distribution App for CMPUT 404, F2021",
        license=openapi.License(name="Apache 2.0")
    ),
    public=True,
    permission_classes=[permissions.AllowAny]
)

app_name = "api"
urlpatterns = [
    path('swagger/', schema_view.with_ui('swagger',
         cache_timeout=0), name='schema-swagger-ui'),
    path('author/<str:author_id>/', views.Author.as_view(), name='author'),
    path('authors/', views.authors, name="authors"),
    # path('author/<str:author_id>/', views.author, name="author"),
    path('author/<str:author_id>/inbox/', views.Inbox.as_view(), name='inbox'),
    path('author/<str:author_id>/post/<str:post_id>/likes', views.Like_Post_API.as_view(), name='like-post'),
    path('author/<str:author_id>/post/<str:post_id>/comment/<str:comment_id>/likes', views.Like_Comment_API.as_view(), name='like-comment'),
    path('author/<str:author_id>/liked', views.Liked_API.as_view(), name='liked'),
    path('author/<str:author_id>/posts/<str:post_id>/comments', views.Comment_API.as_view(), name='comments'),
    path('posts/<str:post_id>', views.PostAPI.as_view(), name="posts")
]
