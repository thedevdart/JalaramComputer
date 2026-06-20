from django.contrib import admin
from django.urls import include, path

from shop.admin import jalaram_admin

urlpatterns = [
    path('admin/', jalaram_admin.urls),
    path('', include('shop.urls')),
]
