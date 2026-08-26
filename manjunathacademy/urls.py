"""
URL configuration for manjunathacademy project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.static import serve

from myapp.views import page_not_found_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('myapp.urls')),
]

# django.conf.urls.static.static() no-ops when DEBUG=False, which is exactly
# the Railway production setting — so it's bypassed here and wired directly
# to Django's serve view. There's no separate object storage/CDN configured
# for user uploads (logo, course thumbnails, banners, etc.), so this is the
# only thing that makes /media/... URLs resolve in production.
urlpatterns += [
    re_path(r'^%s(?P<path>.*)$' % settings.MEDIA_URL.lstrip('/'), serve, {'document_root': settings.MEDIA_ROOT}),
]

handler404 = 'myapp.views.page_not_found_view'

# DEBUG is forced True above (see settings.py), so Django would normally show
# its technical "page not found" debug page for any unmatched URL — handler404
# is only consulted when DEBUG=False. This catch-all, kept as the very last
# pattern, matches anything nothing else did and renders our own 404 page
# (with a working "back to home" button) instead, in every environment.
urlpatterns += [
    re_path(r'^.*$', page_not_found_view),
]
