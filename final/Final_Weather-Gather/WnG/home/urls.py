from django.urls import path
from . import views

from django.urls import path
from . import views
from home import views as weather_views

app_name = 'weather'

urlpatterns = [
    path('index/', views.home), # 홈 화면
    path('kakaologinhome/', views.kakaologin),
    path('kakaoLoginLogic/', views.kakaoLoginLogic),
    path('kakaoLoginLogicRedirect/', views.kakaoLoginLogicRedirect),
    path('kakaoLogout/', views.kakaoLogout),
    path('kakaomessage_climate/', views.kakaoMessage_climate),
    # path('weather/', weather_views.get_weather), # 날씨 정보
]