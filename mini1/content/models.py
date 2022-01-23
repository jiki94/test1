from django.db import models

# Create your models here.
# Feed라는 클래스를 만들건데 괄호 내용은 상속받는 내용, 상속은 models.Model 안에 코딩된 내용을 가져다 쓰겠다!
# modles의 Model을 상속받아서 괄호안에쓰고 클래스를 만들면 얘가 모델역할을 하는구나라고 생각하자
class Feed(models.Model):
    content = models.TextField() # 글내용, 글자니까 TextField
    image = models.TextField() # 피드 이미지, 주소쓸거라 TextField
    identi= models.CharField(max_length=24) # 글쓴이
    
# BooleanField는 좋아요 여부를 판단하기 위해
# 좋아요를 write하고 update 하는 방식으로 적용 그래서 좋아요 할때 Y, 취소하면 N
class Like(models.Model):
    feed_id = models.IntegerField(default=0)
    identi= models.CharField(max_length=24)
    is_like = models.BooleanField(default=True)

# 북마크를 취소할 수도 있으니 아직 북마크 중인지 여부 판단
class Bookmark(models.Model):
    feed_id = models.IntegerField(default=0)
    identi= models.CharField(max_length=24)
    is_marked = models.BooleanField(default=True)