from django.urls import path
from .views import ToggleBookmark, ToggleLike, UploadFeed, Profile, DeleteFeed # content.views에 있는 uploadFeed를 실행한다

urlpatterns = [
    path('upload', UploadFeed.as_view()),
    path('profile', Profile.as_view()),
    path('delete/<id>', DeleteFeed.as_view()),
    path('like', ToggleLike.as_view()),
    path('bookmark', ToggleBookmark.as_view()),
] 
