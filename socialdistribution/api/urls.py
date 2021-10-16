from django.urls import include, path
from . import views 

app_name="api"
urlpatterns = [
    path('author/<str:author_id>/', views.author, name="author" ),
]
