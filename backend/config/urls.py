"""
URL configuration for config project.

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
<<<<<<< HEAD

=======
>>>>>>> a0d58fa9afcc873fc7ab8213d2b217ff1d3ef21f
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
<<<<<<< HEAD
from django.shortcuts import redirect

urlpatterns = [
    path('', lambda request: redirect('meetagain/')),  # 루트 meetagain
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),             # ★ 사용자 앱
    path('meetagain/', include('meetagain.urls')),     # ★ 메인 앱
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
=======
from django.shortcuts import redirect  # ★ 리다이렉트 함수 import

urlpatterns = [
    path('', lambda request: redirect('meetagain/')),  # ★ 루트 URL로 접속하면 meetagain/로 이동
    path('admin/', admin.site.urls),
    path('meetagain/', include('meetagain.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
>>>>>>> a0d58fa9afcc873fc7ab8213d2b217ff1d3ef21f
