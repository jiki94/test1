"""config URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from django.urls import path, include # include 쓰면 딴 장고앱에 있는 urls를 불러올 수 있음
from content.views import Main # content 안에 있는 views에서 Main을 가져온다
from django.conf.urls.static import static
from .settings import MEDIA_URL, MEDIA_ROOT

urlpatterns = [
    path('admin/', admin.site.urls),
    path('main/', Main.as_view()), # main으로 들어갈 때 마다 content 안에 views가 실행 그리고 실행될때마다 Feed에 있는 전체 데이터를 긁어옴
    path('content/', include('content.urls')),
    path('user/', include('user.urls')),
] 


# media에 이미지파일 올리면 그 이미지 파일을 조회할 수 있게 해줌
urlpatterns += static(MEDIA_URL, document_root=MEDIA_ROOT)