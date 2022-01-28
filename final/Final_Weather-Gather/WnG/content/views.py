from django.shortcuts import redirect, render

# Create your views here.
import profile
from django.http import request
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from uuid import uuid4
from user.models import User
from .models import Feed, Like, Bookmark
import os
# config.settings에서 MEDIA_ROOT 가져올꺼임
from config.settings import MEDIA_ROOT 
#2. 그러기위해선 일단 모델에 있는 객체를 다 가져와야함, 모델에서 Feed를 가져올거야
#3. .models가 의미하는건 나랑 같은 폴더안에 있는 models를 의미, 모델쓰고싶으면 이렇게 출처를 적어야함 

# content에 쓸 내용을 html 따로 안만들고 여기다가 만듦

class Main(APIView):
    def get(self, request):
        
        identi = request.session.get('identi', None)
        
        feed_object_list = Feed.objects.all().order_by('-id')
        feed_list = []
        #1. Feed에 있는 모든 데이터를 가져오겠다라는 의미 그리고 이걸 feed_list에 담겠다
        # 즉, Feed의 객체들의 모든 것을 담겠다! 이는 쿼리셋으로 select * from content_feed; 랑 같은 의미
        # order_by('-id') 의미는 객체를 가져올 때 123 순서로 가져오기 때문에 최신글이 밑으로 내려감 그래서 id역순으로 데이터를 가져오게함
        
        # for feed in feed_list:  ---> 뭐 들어있나 궁금할때 해보는 것, for문은 feed_list에 있는거 하나하나 루프를 돔
        #    print(feed.content)  ---> for문을 돌면서 feed_list안에 있는 feed들의 글 내용을 출력 feed.content를 써주면 [<Feed: Feed object(1)>, <Feed: Feed object(2)>] 이딴식으로 출력안하고 DB에 넣은 값이 그대로 보이게됨 
        
        # context로 데이터 넣어줄 때는 딕셔너리형태로 할 것, 실제로 필요한 데이터는 json형태이지만 딕셔너리가 json이랑 호환이됨
        # 앞에 키값은 맘대로 넣어도 됨(지금은 feeds라고 임의로 이름 지음) 하지만 value값인 feed_list는 위에서 Feed.objects.all()에서 가져오는 것이므로 변경불가 
        
        # 글을 쓰고나서 프로필을 바꿔도 실시간으로 갱신하게해줌
        # feed_list를 내려줄 때 사용자가 feed를 좋아요 눌렀는지 안눌렀는지를 표시해줘야함 즉, 내가 이 feed에 대해서 좋아요 눌렀는지 안눌렀는지에 대한 데이터가 있어야함
        query = request.GET.get('q', None)

        for feed in feed_object_list:
            user = User.objects.filter(identi=feed.identi).first()
            if query is None or query in feed.content:
                #내가 쓴게 내가 이 feed_id에 대해서 좋아요를 누른게 있으면 exist
                #그래서 내가 좋아요를 눌렀으면 is_liked는 False가 됨
                like_count = Like.objects.filter(feed_id=feed.id, is_like=True).count()
                is_liked=Like.objects.filter(feed_id=feed.id, identi=identi, is_like=True).exists()
                is_marked=Bookmark.objects.filter(feed_id=feed.id, identi=identi, is_marked=True).exists()
                feed_list.append(dict(image=feed.image,
                                    content=feed.content,   
                                    profile_image=user.profile_image,
                                    nickname=user.nickname,
                                    id=feed.id,
                                    like_count=like_count,
                                    is_liked=is_liked,
                                    is_marked=is_marked
                                    ))
        # 세션에 담았으므로 이제 유저 정보가 하드코딩되지않고 쓸수있게됨
        # 로그인하고 다른 사이트 갔다가 /main으로 다시 와도 세션정보 남아서 로그인 유지됨
        # 반대로 로그아웃한다음 다른 사이트 갔다가 /main 들어가면 세션정보가 없어서 로그인창 뜨게됨
        
        #만약 로그인을 안하고 /main에 접속한 경우 로그인하라고 함
        if identi is None:
            return render(request, "user/tempLogin.html")
        
        user = User.objects.filter(identi=identi).first()
        
        #만약 세션정보에 아이디가 이미 있었는데 그 아이디가 회원이 아닌경우
        if user is None:
            return render(request, "user/tempLogin.html")
        
        return render(request, "config/main.html", context=dict(feeds=feed_list, user=user))

# 서버에서 공유하기버튼눌러서 보낸 파일을 받아서 처리하는 걸 만들면됨(main.html에서 콜백함수 쓴 부분)
# 데이터베이스에는 파일이 실제로 들어가지 않고 그 주소만 db에 저장
class UploadFeed(APIView):
    def post(self, request):

# 대문자로 FILES를 해야 file을 불러옴, 업로드할 때 file 리스트를 보내지말고 하나만 보내면되는 상황 
        file = request.FILES['file']
        
#이미지파일 이름들보면 영어숫자특수문자 막 섞여있는데 이거를 프로그램에서 잘 찾을 수 있게 하기위해 영어와 숫자로 이루어진 고유한 id값을 주기위해 사용
#uuid4().hex는 랜덤하게 글자를 만들어줌 
        ext = file.name.split(".")[-1]
        uuid_name = str(uuid4().hex) + "." + str(ext)
        # 파일업로드한 위치는 ~/media에 uuid로 생성된 이름으로 저장
        save_path = os.path.join(MEDIA_ROOT, uuid_name)
        #파일을 읽어서 파일로 만들 때 쓴다고만 알아두자
        with open(save_path, 'wb+') as destination: 
            for chunk in file.chunks():
                destination.write(chunk) 
                #여기까지 수행되면 파일이 media에 저장됨 
        #파일이 media에 저장됐으면 이제 해야할껀 저장된 경로를 image에 저장해야함 그래서 클라이언트가 올린 파일이미지 이름이 필요없어짐
        
        image = uuid_name
        content = request.data.get('content')
        identi = request.session.get('identi', None)
        
        
        #마지막으로 feed에 저장하는 부분
        Feed.objects.create(image=image, content=content, identi=identi)
        
        return Response(status = 200)

class DeleteFeed(APIView):
    def delete(self, request, id):
        if request.session.get('id', None):
            query = Feed.objects.get(id=id)
            query.delete()
        else:
            return redirect('/main')
    
class Profile(APIView):
    def get(self, request):
        identi = request.session.get('identi', None)
        
        #만약 로그인을 안하고 /main에 접속한 경우 로그인하라고 함
        if identi is None:
            return render(request, "user/tempLogin.html")
        
        user = User.objects.filter(identi=identi).first()
        
        #만약 세션정보에 아이디가 이미 있었는데 그 아이디가 회원이 아닌경우
        if user is None:
            return render(request, "user/tempLogin.html")
        # like_feed_list(내가 좋아요를 누른 피드리스트)는 피드에서 내가 좋아요를 누른 id값이 내가 좋아요를 누른 리스트에 있는거
        # id__n 은 Feed에 있는 id중에 feed id 리스트를 포함하고 있는 것만 걸림
        # flat = True 안하면 리스트로 안나옴
        feed_list = Feed.objects.filter(identi=identi).all()
        like_list = list(Like.objects.filter(identi=identi, is_like=True).values_list('feed_id', flat = True))
        like_feed_list = Feed.objects.filter(id__in=like_list)
        bookmark_list = list(Bookmark.objects.filter(identi=identi, is_marked=True).values_list('feed_id', flat = True))
        bookmark_feed_list = Feed.objects.filter(id__in=bookmark_list)
        return render(request, 'content/profile.html', context=dict(feed_list=feed_list,
                                                                    like_feed_list=like_feed_list,
                                                                    bookmark_feed_list=bookmark_feed_list,
                                                                    user=user))
    
class ToggleLike(APIView):
    def post(self, request):
        feed_id = request.data.get('feed_id', None)
        favorite_text = request.data.get('favorite_text', True)
        
        
        if favorite_text == 'favorite_border':
            is_like = True
        else:
            is_like = False
        identi = request.session.get('identi', None)
        
        like = Like.objects.filter(feed_id=feed_id, identi=identi).first()
        
        if like:
            like.is_like = is_like
            like.save()
        else:
            Like.objects.create(feed_id=feed_id, is_like=is_like, identi=identi)
        
        return Response(status=200)
    
class ToggleBookmark(APIView):
    def post(self, request):
        feed_id = request.data.get('feed_id', None)
        bookmark_text = request.data.get('bookmark_text', True)
        
        
        if bookmark_text == 'bookmark_border':
            is_marked = True
        else:
            is_marked = False
        identi = request.session.get('identi', None)
        
        bookmark = Bookmark.objects.filter(feed_id=feed_id, identi=identi).first()
        
        if bookmark:
            bookmark.is_marked = is_marked
            bookmark.save()
        else:
            Bookmark.objects.create(feed_id=feed_id, is_marked=is_marked, identi=identi)
        
        return Response(status=200)