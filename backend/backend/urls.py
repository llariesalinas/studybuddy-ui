"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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
from django.http import HttpResponse
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


def healthz(request):
    # Liveness check for Render (and similar platforms). No DB query, no auth --
    # exempted from DemoBasicAuthMiddleware so the platform's health checker
    # (which never sends Basic Auth credentials) doesn't get marked unhealthy.
    return HttpResponse('ok')


urlpatterns = [
    path('healthz', healthz),
    path('admin/', admin.site.urls),
    path('api/', include('studybuddy.urls')),
]

# Serves uploaded media (avatars, application documents) unconditionally, not just under DEBUG.
# Django's own docs discourage this for real production (no caching/CDN, single-process request
# handling), but this app has no separate media host (S3, etc.) configured, and DEBUG=False on the
# demo deployment for production-style security meant this block never ran there -- every image
# 404'd. Revisit with a real media host before this settings file is reused for real production.
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
