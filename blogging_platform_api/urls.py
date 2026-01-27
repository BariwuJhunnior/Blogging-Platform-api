from django.contrib import admin
from django.urls import path, include
#IMAGEFIELD IMPORTS FOR DISPLAYING PROFILE PICTURE
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse

def home(request):
    return JsonResponse({
        "message": "Blogging Platform API is running!",
        "/api/": "Append to end of url to list endpoints"
    })

def api_root(request):
    return JsonResponse({
        "Message": "Welcome to the Blogging Platform API",
        "Endpoints": {
            "Users": "/api/users/",
            "Register": "/api/register/",
            "Login": "/api/login/",
            "Posts": "/api/posts/",
            "Feed": "/api/feed/",
            "API Documentation": "/api/docs/swagger"
        }
    })


urlpatterns = [
    path("", home),
    path("api/", api_root),
    path('admin/', admin.site.urls),
    path('api/', include('users.urls')),
    path('api/', include('posts.urls')),
]
