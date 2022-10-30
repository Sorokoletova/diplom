"""todolist URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from todolist.views import health_check
from core import views
from goals import views
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('ping/', health_check, name='health_check'),
    path('core/', include('core.urls')),
    path('oauth/', include('social_django.urls', namespace='social')),
    path("goals/", include("goals.urls")),
    path('bot/', include('bot.urls')),

]
