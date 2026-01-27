from django.contrib import admin
from django.urls import path, include
#IMAGEFIELD IMPORTS FOR DISPLAYING PROFILE PICTURE
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse

def home(request):
    return JsonResponse({
        "message": "Blogging Platform API is running!",
        "/api/": "To List Endpoints"
    })

def api_root(request):
    return JsonResponse({
        "message": "Welcome to the Blogging Platform API",
        "endpoints": {
            "users": "/api/users/",
            "register": "/api/register/",
            "login": "/api/login/",
            "posts": "/api/posts/",
            "feed": "/api/feed/",
            "docs": "/api/docs/swagger"
        }
    })


urlpatterns = [
    path("", home),
    path("api/", api_root),
    path('admin/', admin.site.urls),
    path('api/', include('users.urls')),
    path('api/', include('posts.urls')),
]
