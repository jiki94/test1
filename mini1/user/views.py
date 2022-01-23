import profile
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import User
from uuid import uuid4
import os
from config.settings import MEDIA_ROOT
from django.contrib.auth.hashers import make_password

# Create your views here.
# Join이라는 함수 실행하면 get으로 호출했을 때 user앱 폴더에 있는 join.html을 보여줘라
class Join(APIView):
    def get(self, request):
        return render(request, "user/join.html")
    
    def post(self, request):
        # TODO 회원가입, 단방향은 암호화만되고 양방향은 복호화도 가능, 비밀번호는 직원도 몰라야하니 단방향
        # 회원가입을 만들었으니 화면에서 실제로 올리면됨 그러기 위해서 html에서 ajax통신을 만들자
        identi = request.data.get('identi', None)
        nickname = request.data.get('nickname', None)
        age = request.data.get('age', None)
        password = request.data.get('password', None)
        
        User.objects.create(identi=identi, 
                            nickname=nickname, 
                            age= age, 
                            password= make_password(password),
                            profile_image="default_profile.png")
        
        return Response(status=200)

class Login(APIView):
    def get(self, request):
        return render(request, "user/login.html")

    def post(self, request):
        #TODO 로그인
        identi = request.data.get('identi', None)
        password = request.data.get('password', None)
        # filter는 쿼리셋을 리턴함 그래서 하나든 두개든 리스트형태로 리턴함 
        # first()를 해주면 하나만 선택해줌 그래서 하나면 하나리턴 두개면 첫번째거 하나를 리턴
        # 이렇게 되면 리스트객체인 user_list를 쓰지 않고 user 객체를 쓸수있음
        user = User.objects.filter(identi=identi).first()
        
        if user is None:
            return Response(status=400, data=dict(message="회원정보가 잘못되었습니다."))
        
        if user.check_password(password):
            # 세션에 사용자아이디인 identi 넣음
            # session['identi'] 찾으면 내가 저장한 아이디가 나온다
            # 아이디를 세션정보에 넣게 되면 아이디를 가지고 user=User.objects.filter() 해서 
            # user의 닉네임이나 나이 등을 가져올 수 있게 됨   
            request.session['identi'] = identi
            return Response(status=200)
        else:
            return Response(status=400, data=dict(message="회원정보가 잘못되었습니다."))
        
class Logout(APIView):
    def get(self, request):
        request.session.flush()
        return render(request, "user/login.html")

# UploadProfile 로직은 파일이랑 아이디를 불러옴
# 파일은 Feed 생성할 때 처럼 이미지 이름바꿔주는방식으로 랜덤으로 고유값 만들어주고 media에 저장
# 파일이름을 profile_image 필드에 저장한다음 올라온 아이디주소로 사용자를 찾아서
# 사용자의 프로필 이미지에 profile_image를 저장해주고 user.save()를 하면 DB에 저장
class UploadProfile(APIView):
    def post(self, request):

        #파일 불러옴
        file = request.FILES['file']
        identi = request.data.get('identi')
        
        uuid_name = uuid4().hex
        save_path = os.path.join(MEDIA_ROOT, uuid_name)

        with open(save_path, 'wb+') as destination: 
            for chunk in file.chunks():
                destination.write(chunk) 
        
        profile_image = uuid_name
        
        # 유저에서 필터로 identi가 identi인 사람 찾아서 그 유저의 프로필 이미지를 바꿔줌 그리고 create 경우에는 자동으로 생성되니까 save 안하지만
        # 객체를 불러와서 그 안에 있는 데이터를 수정하는 경우 save 필요
        user = User.objects.filter(identi=identi).first()
        
        user.profile_image = profile_image
        user.save()

        return Response(status = 200)