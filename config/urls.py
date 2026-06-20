from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from django.views.static import serve

urlpatterns = [
    path('django-admin/', admin.site.urls),
    path('', include('shop.urls')),
]

# Serve /data/ and root-level public files (hero-services.json, admin assets path handled separately)
urlpatterns += [
    path('data/<path:path>', serve, {'document_root': settings.PUBLIC_DIR / 'data'}),
]
