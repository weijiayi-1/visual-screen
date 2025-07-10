"""
URL configuration for myproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.urls import path
from myapp.views import city_table, city_data_api, map3d_data_api

urlpatterns = [
    path("admin/", admin.site.urls),
    path("city_table/", city_table, name="city_table"),
    path("api/city_data/", city_data_api, name="city_data_api"),
    path("api/map3d_data/", map3d_data_api, name="map3d_data_api"),
]
