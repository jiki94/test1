from django.urls import path
from .views import UploadFeed, Profile # content.views에 있는 uploadFeed를 실행한다

urlpatterns = [
    path('upload', UploadFeed.as_view()),
    path('profile', Profile.as_view()),
] 
