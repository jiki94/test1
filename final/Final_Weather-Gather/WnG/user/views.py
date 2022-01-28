import profile
from django.shortcuts import redirect, render
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
        return render(request, "user/tempJoin.html")
        #return render(request, "user/join.html")
    
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
        #return render(request, "user/login.html")
        return render(request, "user/tempLogin.html")

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
            request.session['identi'] = user.identi
            return Response(status=200)
        else:
            return Response(status=400, data=dict(message="회원정보가 잘못되었습니다."))
        
class Logout(APIView):
    def get(self, request):
        request.session.flush()
        #return render(request, "user/login.html")
        return render(request, "user/tempLogin.html")

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



#KAKAO API 
#카카오 로그인
import requests
import json
from django.template import loader
from django.http import HttpResponse, JsonResponse

# Create your views here.
# class Kakao(APIView):
#     def kakaologinHome(self, request):
#         _context = {'check':False}
#         if request.session.get('access_token'):
#             _context['check'] = True
#         return render(request, 'user/kakaologin.html', _context)

#     def kakaoLoginLogic(self, request):
#         _restApiKey = '5d03e24af9d6c95a6f526e3308d8879d' # 입력필요
#         _redirectUrl = 'http://127.0.0.1:8000/kakao/kakaoLoginLogicRedirect'
#         _url = f'https://kauth.kakao.com/oauth/authorize?client_id={_restApiKey}&redirect_uri={_redirectUrl}&response_type=code'
#         return redirect(_url)

#     def kakaoLoginLogicRedirect(self, request):
#         _qs = request.GET['code']
#         _restApiKey = '5d03e24af9d6c95a6f526e3308d8879d' # 입력필요
#         _redirect_uri = 'http://127.0.0.1:8000/kakao/kakaoLoginLogicRedirect'
#         _url = f'https://kauth.kakao.com/oauth/token?grant_type=authorization_code&client_id={_restApiKey}&redirect_uri={_redirect_uri}&code={_qs}'
#         _res = requests.post(_url)
#         _result = _res.json()
#         request.session['access_token'] = _result['access_token']
#         request.session.modified = True
#         return render(request, 'user/kakaologinSuccess.html')

#     def kakaoLogout(self, request):
#         _token = request.session['access_token']
#         _url = 'https://kapi.kakao.com/v1/user/logout'
#         _header = {
#             'Authorization': f'bearer {_token}'
#         }
#             # _url = 'https://kapi.kakao.com/v1/user/unlink'
#             # _header = {
#             #   'Authorization': f'bearer {_token}',
#             # }
#         _res = requests.post(_url, headers=_header)
#         _result = _res.json()
#         if _result.get('id'):
#             del request.session['access_token']
#             return render(request, 'user/kakaologinoutSuccess.html')
#         else:
#             return render(request, 'user/kakaologoutError.html')

#         #날씨 요약 정보
#     def kakaoMessage_climate(self, request):
#         temperature = 24
#         rain = 30
#         cloth = ""

#         if temperature <= 4:
#             cloth = "패딩, 목도리, 장갑 매우 추워요"
#         elif temperature >= 5 and temperature <= 8:
#             cloth = "울코트, 기모"
#         elif temperature >= 9 and temperature <= 11:
#             cloth = "트렌치 코트, 점퍼"
#         elif temperature >= 12 and temperature <= 16:
#             cloth = "가디건, 청자켓, 청바지"
#         elif temperature >= 17 and temperature <= 19:
#             cloth = "후드티, 맨투맨"
#         elif temperature >= 20 and temperature <= 22:
#             cloth = "블라우스, 슬랙스"
#         elif temperature >= 23 and temperature <= 27:
#             cloth = "반팔, 반바지, 얇은 셔츠"
#         else:
#             cloth = "시원하게 입기"



#         url_message = "https://kapi.kakao.com/v2/api/talk/memo/default/send"

#         _token = request.session['access_token']

#         _header = {
#             'Authorization': f'bearer {_token}'
#         }
            
#             # _nickname = "희동이누나"    #String
#             # _today = "오늘의 날씨입니다."   #String

#         data={
#             "template_object": json.dumps({
#                 "object_type": "text",
#                 "text": "오늘의 날씨 요약 정보는 \n" + "기온 : " + (str)(temperature) + "'C\n강수확률 : " + (str)(rain) + "% 이므로\n오늘의 옷차림은 " + cloth + "를 추천드립니다.",
#                 "link":{
#                     "web_url":"http://127.0.0.1:8000/user/login"
#                 }
#             })
#         }

#             # data = {
#             #     "template_object" : json.dumps({
#             #         "object_type": "list",
#             #         "header_title": "오늘의 날씨입니다.",
#             #         "header_link" : "http://127.0.0.1:8000/kakao/home",
#             #         "contents" : climate
#             #     })
#             # }

#             # print(climate_list)

#         _res = requests.post(url_message, headers=_header, data=data)
#         _result = _res.json()
#         return render(request, 'user/kakaoclimatemessage.html')

#         #패스워드 찾기
#     def password_throw(self, request):
#         return render(request, 'user/kakaopassword.html')
#             # return render(request, 'kakaoproejct/passwordcheck.html')

#         # def password_check(request):
#         #     me = (str)(request.GET.get('me'))
#         #     ID = User.objects.filter(user_identi = me).values("user_identi")

#         #     if ID == '':
#         #         return render(request, 'kakaoproject/passwordError.html')
#         #     else:
#         #         return render(request, 'kakaoproject/passwordSuccess.html', {'me' : me})

#     def kakaoMessage_password(self, request):
#         me = (str)(request.GET.get('me'))
#         ID = (str)(list(User.objects.filter(user_identi = me).values("user_identi")))
#         password = (str)(list(User.objects.filter(user_identi = me).values("password")))

#         url_message = "https://kapi.kakao.com/v2/api/talk/memo/default/send"

#         _token = request.session['access_token']

#         _header = {
#             'Authorization': f'bearer {_token}'
#         }

#         data={
#             "template_object": json.dumps({
#                 "object_type": "text",
#                 "text": ID + "님 패스워드는 " + password + "입니다.",
#                 "link":{
#                     "web_url":"http://127.0.0.1:8000/user/login"
#                 }
#             })
#         }

#         _res = requests.post(url_message, headers=_header, data=data)
#         _result = _res.json()
#         return render(request, 'user/kakaopasswordSuccess.html')


def kakaologinHome(request):
    _context = {'check':False}
    if request.session.get('access_token'):
        _context['check'] = True
    return render(request, 'user/kakaologin.html', _context)

def kakaoLoginLogic(request):
    _restApiKey = '5d03e24af9d6c95a6f526e3308d8879d' # 입력필요
    _redirectUrl = 'http://127.0.0.1:8000/kakao/kakaoLoginLogicRedirect'
    _url = f'https://kauth.kakao.com/oauth/authorize?client_id={_restApiKey}&redirect_uri={_redirectUrl}&response_type=code'
    return redirect(_url)

def kakaoLoginLogicRedirect(request):
    _qs = request.GET['code']
    _restApiKey = '5d03e24af9d6c95a6f526e3308d8879d' # 입력필요
    _redirect_uri = 'http://127.0.0.1:8000/kakao/kakaoLoginLogicRedirect'
    _url = f'https://kauth.kakao.com/oauth/token?grant_type=authorization_code&client_id={_restApiKey}&redirect_uri={_redirect_uri}&code={_qs}'
    _res = requests.post(_url)
    _result = _res.json()
    request.session['access_token'] = _result['access_token']
    request.session.modified = True
    return render(request, 'user/kakaologinSuccess.html')

def kakaoLogout(request):
    _token = request.session['access_token']
    _url = 'https://kapi.kakao.com/v1/user/logout' 
    _header = {
        'Authorization': f'bearer {_token}'
    }
            # _url = 'https://kapi.kakao.com/v1/user/unlink'
            # _header = {
            #   'Authorization': f'bearer {_token}',
            # }
    _res = requests.post(_url, headers=_header)
    _result = _res.json()
    if _result.get('id'):
        del request.session['access_token']
        return render(request, 'user/kakaologinoutSuccess.html')
    else:
        return render(request, 'user/kakaologoutError.html')

        #날씨 요약 정보
def kakaoMessage_climate(request):
    temperature = 24
    rain = 30
    cloth = ""

    if temperature <= 4:
        cloth = "패딩, 목도리, 장갑 매우 추워요"
    elif temperature >= 5 and temperature <= 8:
        cloth = "울코트, 기모"
    elif temperature >= 9 and temperature <= 11:
        cloth = "트렌치 코트, 점퍼"
    elif temperature >= 12 and temperature <= 16:
        cloth = "가디건, 청자켓, 청바지"
    elif temperature >= 17 and temperature <= 19:
        cloth = "후드티, 맨투맨"
    elif temperature >= 20 and temperature <= 22:
        cloth = "블라우스, 슬랙스"
    elif temperature >= 23 and temperature <= 27:
        cloth = "반팔, 반바지, 얇은 셔츠"
    else:
        cloth = "시원하게 입기"



    url_message = "https://kapi.kakao.com/v2/api/talk/memo/default/send"

    _token = request.session['access_token']

    _header = {
        'Authorization': f'bearer {_token}'
    }
            
            # _nickname = "희동이누나"    #String
            # _today = "오늘의 날씨입니다."   #String

    data={
        "template_object": json.dumps({
            "object_type": "text",
            "text": "오늘의 날씨 요약 정보는 \n" + "기온 : " + (str)(temperature) + "'C\n강수확률 : " + (str)(rain) + "% 이므로\n오늘의 옷차림은 " + cloth + "를 추천드립니다.",
            "link":{
                "web_url":"http://127.0.0.1:8000/user/login"
            }
        })
    }

            # data = {
            #     "template_object" : json.dumps({
            #         "object_type": "list",
            #         "header_title": "오늘의 날씨입니다.",
            #         "header_link" : "http://127.0.0.1:8000/kakao/home",
            #         "contents" : climate
            #     })
            # }

            # print(climate_list)

    _res = requests.post(url_message, headers=_header, data=data)
    _result = _res.json()
    return render(request, 'user/kakaoclimatemessage.html')

        #패스워드 찾기
def password_throw(request):
    return render(request, 'user/kakaopassword.html')
            # return render(request, 'kakaoproejct/passwordcheck.html')

        # def password_check(request):
        #     me = (str)(request.GET.get('me'))
        #     ID = User.objects.filter(user_identi = me).values("user_identi")

        #     if ID == '':
        #         return render(request, 'kakaoproject/passwordError.html')
        #     else:
        #         return render(request, 'kakaoproject/passwordSuccess.html', {'me' : me})

def kakaoMessage_password(request):
    me = (str)(request.GET.get('me'))
    ID = (str)(list(User.objects.filter(user_identi = me).values("user_identi")))
    password = (str)(list(User.objects.filter(user_identi = me).values("password")))

    url_message = "https://kapi.kakao.com/v2/api/talk/memo/default/send"

    _token = request.session['access_token']

    _header = {
        'Authorization': f'bearer {_token}'
    }

    data={
        "template_object": json.dumps({
            "object_type": "text",
            "text": ID + "님 패스워드는 " + password + "입니다.",
            "link":{
                "web_url":"http://127.0.0.1:8000/user/login"
            }
        })
    }

    _res = requests.post(url_message, headers=_header, data=data)
    _result = _res.json()
    return render(request, 'user/kakaopasswordSuccess.html')

from django.contrib import messages
from django.contrib.auth import logout

def profile_delete_view(request):
    if request.method == 'POST':
        logout(request)
        messages.success(request, "회원탈퇴 완료.")
        return redirect('/user/login')

    return render(request, 'profile_delete.html', {})    
