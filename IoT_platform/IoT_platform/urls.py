"""IoT_platform URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.urls import include, path
from rest_framework import routers
from database.views import *
from rest_framework.authtoken import views
from django.conf.urls.static import static

admin.site.site_header = "IoT platform Backend Administration"
admin.site.site_title = admin.site.site_header

router = routers.DefaultRouter(trailing_slash=False)
router.register("parameters",ParameterViewSet,"parameters")
router.register("sensors",SensorViewSet,"sensors")
router.register("sensorvalues",SensorvalueViewSet,"sensorvalues")
router.register("users",UserViewSet,"users")

urlpatterns = [
    path('authenticate', views.obtain_auth_token),
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('database/', include('database.urls')),
]
