from django.contrib import admin
from django.urls import path
from django.urls import re_path
from django.urls import include
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    re_path(r'^_nested_admin/', include('nested_admin.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# BotEngine().start_bot()

# Dont forget about users logs