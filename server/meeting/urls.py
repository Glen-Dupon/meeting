# encoding: utf-8
from __future__ import absolute_import, unicode_literals

from django.conf.urls.static import static

"""ballcall URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/dev/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.urls import include, path
from django.contrib import admin

from core.utils import get_api_js

#product static import
#from django.urls import include, path
#from django.views.static import serve as static_serve 

api_patterns = [
    # 官方文档没有讲这样的写法：
    path('wechat/', include("apps.wechat.views")),
    path('ballcall/', include("apps.ballcall.views")),

    # path('wechat/', include("apps.wechat.urls")),
    # path('ballcall/', include("apps.ballcalls.urls")),

]

urlpatterns = [
    #product static setting
    #re_path(r'^static/(?P<path>.*)$', static_serve, {'document_root' : settings.STATIC_ROOT}),
    path('cool/', include('cool.urls')),
    path('sysadmin/', admin.site.urls),
    path('api/', include(api_patterns)),
    # path('wsapi/', include(api_patterns)),
]
if settings.DEBUG:
    urlpatterns.append(path('api.js', get_api_js))
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
