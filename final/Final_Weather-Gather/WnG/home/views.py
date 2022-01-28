from os import TMP_MAX
from django.shortcuts import render
from numpy import identity
import requests
import json
from datetime import date, datetime, timedelta, time
import urllib
import urllib.request
import math

from django.shortcuts import redirect
from django.template import loader
from django.http import HttpResponse, JsonResponse
import requests

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model

from user.models import User

# from django.contrib.auth.models import User

# google api geolocate를 활용하여 ip 주소를 기반으로 현재 위치의 위도, 경도 정보 추출
def get_location(request):
    url = f'https://www.googleapis.com/geolocation/v1/geolocate?key=AIzaSyBf9kIq9ciMUvzAr5neaJRMrlbx7rMZJx0'
    data = {'considerIp': True, } # 현 IP로 데이터 추출
    result = requests.post(url, data) # 해당 API에 요청을 보내며 데이터를 추출
    print(result.text)
    result2 = json.loads(result.text)

    lat = result2["location"]["lat"] # 현재 위치의 위도 추출
    lng = result2["location"]["lng"] # 현재 위치의 경도 추출

    return lat, lng


#get_location함수를 통해 위도와 경도 값을 넣고 x좌표, y좌표 얻어내기
def grid(lat, lng):
    v1 = lat
    v2 = lng

    Re = 6371.00877     ##  지도반경
    grid = 5.0          ##  격자간격 (km)
    slat1 = 30.0        ##  표준위도 1
    slat2 = 60.0        ##  표준위도 2
    olon = 126.0        ##  기준점 경도
    olat = 38.0         ##  기준점 위도
    XO = 43             ##  기준점 X좌표
    YO = 136            ##  기준점 Y좌표
    DEGRAD = math.pi / 180.0

    re = Re / grid
    slat1 = slat1 * DEGRAD  #표준위도1
    slat2 = slat2 * DEGRAD  #표준위도2
    olon = olon * DEGRAD    #기준점 경도
    olat = olat * DEGRAD    #기준점 위도

    sn = math.tan(math.pi * 0.25 + slat2 * 0.5) / math.tan(math.pi * 0.25 + slat1 * 0.5)  
    sn = math.log(math.cos(slat1) / math.cos(slat2)) / math.log(sn)
    sf = math.tan(math.pi * 0.25 + slat1 * 0.5)  
    sf = math.pow(sf, sn) * math.cos(slat1) / sn
    ro = math.tan(math.pi * 0.25 + olat * 0.5)   
    ro = re * sf / math.pow(ro, sn)
    ra = math.tan(math.pi * 0.25 + (v1) * DEGRAD * 0.5)
    ra = re * sf / math.pow(ra, sn)

    theta = v2 * DEGRAD - olon

    if theta > math.pi :
        theta -= 2.0 * math.pi
    if theta < -math.pi :
        theta += 2.0 * math.pi
    theta *= sn

    x = math.floor(ra * math.sin(theta) + XO + 0.5)
    y = math.floor(ro - ra * math.cos(theta) + YO + 0.5)

    # x좌표, y좌표 리턴
    return x, y    

def home(request):
    #위도, 경도 함수 호출
    lat, lng = get_location(request)
    # print(lat, lng)

    # x좌표, y좌표 함수 호출
    x, y = grid(lat, lng)
    # print(x,y)

    # 기상청 단기예보 api
    url = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst"

    today = datetime.now()

    base_date = today.strftime("%Y%m%d")
    today_date = today.strftime("%Y%m%d")
    tomorrow = date.today() + timedelta(days=1)
    tomorrow_date = tomorrow.strftime("%Y%m%d")
    yesterday = date.today() - timedelta(days=1)
    yesterday_date = yesterday.strftime("%Y%m%d")
    
    
    time = today.strftime('%H%M')
    
    
    
    # 날씨 정보 발표 날짜와 시각(base_date, base_time) 
    # 하드코딩 대신 자동으로 시간 받아서 설정해주기

    hour = today.hour
    minute = today.minute
    # print(time)
    if hour < 2 or (hour == 2 and minute <= 10): # 00:00 1:59
        base_date = yesterday_date
        base_time = "2300"
    elif hour < 5 or (hour == 5 and minute <= 10):
        base_date = today_date
        base_time = "0200"
    elif hour < 8 or (hour == 8 and minute <= 10): # 5시 11분~8시 10분 사이
        base_date = today_date
        base_time = "0500"
    elif hour<11 or (hour == 11 and minute <=10): # 8시 11분~11시 10분 사이
        base_date = today_date
        base_time = "0800"
    elif hour < 14 or (hour == 14 and minute <= 10): # 11시 11분~14시 10분 사이
        base_date = today_date
        base_time = "1100"
    elif hour < 17 or (hour == 17 and minute <= 10): # 14시 11분~17시 10분 사이
        base_date = today_date
        base_time = "1400"
    elif hour < 20 or (hour == 20 and minute <= 10): # 17시 11분~20시 10분 사이
        base_date = today_date
        base_time ="1700" 
    elif hour < 23 or (hour == 23 and minute <= 10): # 20시 11분~23시 10분 사이
        base_date = today_date
        base_time ="2000"
    else: # 23시 11분~23시 59분
        base_date = today_date
        base_time = "2300"



    # 지금 현재 날씨 정보 제공 내일 출근 날씨 제공 json 정보 불러오기

    params ={'serviceKey' : 'Rty09EbsqEEgCQyDM03L//hEwSnSIENiavOyVF3BsZwUSxzkFNKrJFgbXTSayi81l4WbTijUpuHbow5W/FwB4w==', 
        'pageNo' : '1', 'numOfRows' : '1000', 'dataType' : 'JSON',
        'base_date' : base_date, 'base_time' : base_time, 'nx' : x, 'ny' : y}


    res = requests.get(url, params=params)

    #json 값에서 item 뽑기

    r_dict = json.loads(res.text)
    r_response = r_dict.get("response")
    r_body = r_response.get("body")
    r_items = r_body.get("items")
    r_item = r_items.get("item")

    # item에 있는 여러 값들 중에 필요한 날씨 데이터 뽑아내기

    # 현재 시간의 날씨 정보 data에 저장
    today = {}
    

    # today에 현재 시간의 날씨 정보 담기(현재 시간을 계산해서 
    # 예보 시각(fcstTime)에 맞는 날씨 정보 담기)
    # base_date = yesterday_date
    # base_time = "2300"
    
    # 0000
    # 0100
    # 0200
    # 0300
    # ....
    # 2358
    # 0008
    # 1754
    # 1700+100
    # 1700

    # 1800
    # 1900
    # 2000

   
    if 0<= int(time) // 100 <=8 :
        fcstTime = '0' + str(int(time) // 100 * 100 + 100)

    else :
        if int(time) // 100 == 23:
            fcstTime = "0000"
            today_date = tomorrow_date
        else:
            fcstTime = str(int(time) // 100 * 100  + 100)


    for item in r_item:
        if(item.get("fcstDate") == today_date and item.get("fcstTime") == fcstTime and item.get("category") == "TMP"):
            today['기온'] = item["fcstValue"] 

        if(item.get("fcstDate") == today_date and item.get("fcstTime") == fcstTime and item.get("category") == "PTY"):
            rainfall_code = item.get("fcstValue") 

            if rainfall_code == '1':
                rainfall_state = '비'

            elif rainfall_code == '2':
                rainfall_state = '비/눈'

            elif rainfall_code == '3':
                rainfall_state = '눈'

            elif rainfall_code == '4':
                rainfall_state = '소나기'

            else:
                rainfall_state = '없음'

            today['눈/비 소식'] = rainfall_state

        if(item.get("fcstDate") == today_date and item.get("fcstTime") == fcstTime and item.get("category") == "POP"):
            today['강수확률'] = item["fcstValue"]

        if(item.get("fcstDate") == today_date and item.get("fcstTime") == fcstTime and item.get("category") == "REH"):
            today['습도'] = item["fcstValue"] + '%'

        if(item.get("fcstDate") == today_date and item.get("fcstTime") == fcstTime and item.get("category") == "WSD"):
            today['풍속'] = item["fcstValue"] + 'm/s'

        if(item.get("fcstDate") == today_date and item.get("fcstTime") == fcstTime and item.get("category") == "SKY"):
            weather_code = item.get("fcstValue")

            if weather_code == '1':
                weather_state = '맑음'

            elif weather_code == '3':
                weather_state = '구름많음'

            else:
                weather_state = '흐림'

            today['날씨'] = weather_state


    tmp = int(today['기온'])
    sky = today['날씨']
    pty = today['눈/비 소식']
    pop = int(today['강수확률'])
    wsd = today['풍속']
    reh = today['습도']

    global temperature
    temperature = tmp
    global rain
    rain = pop


    # today_result에 현재 날씨 정보 

    today_result = []
    today_result.append(tmp)
    today_result.append(sky)
    today_result.append(pty)
    today_result.append(pop)
    today_result.append(wsd)
    today_result.append(reh)
    today_result.append(today_date)

    
    # 다음날 출근 시간(0700)을 기준으로 날씨 정보 받아오기
    tomorrow = {}

    for item in r_item:
        if(item.get("fcstTime") == "0700" and item.get("fcstDate") == tomorrow_date and item.get("category") == "TMP"):
            tomorrow['기온'] = item["fcstValue"]

        if(item.get("fcstTime") == "0700" and item.get("fcstDate") == tomorrow_date and item.get("category") == "PTY"):
            rainfall_code = item.get("fcstValue") 

            if rainfall_code == '1':
                rainfall_state = '비'

            elif rainfall_code == '2':
                rainfall_state = '비/눈'

            elif rainfall_code == '3':
                rainfall_state = '눈'

            elif rainfall_code == '4':
                rainfall_state = '소나기'

            else:
                rainfall_state = '없음'

            tomorrow['눈/비 소식'] = rainfall_state

        if(item.get("fcstTime") == "0700" and item.get("fcstDate") == tomorrow_date and item.get("category") == "POP"):
            tomorrow['강수확률'] = item["fcstValue"]

        if(item.get("fcstTime") == "0700" and item.get("fcstDate") == tomorrow_date and item.get("category") == "REH"):
            tomorrow['습도'] = item["fcstValue"] + '%'

        if(item.get("fcstTime") == "0700" and item.get("fcstDate") == tomorrow_date and item.get("category") == "WSD"):
            tomorrow['풍속'] = item["fcstValue"] + 'm/s'

        if(item.get("fcstTime") == "0700" and item.get("fcstDate") == tomorrow_date and item.get("category") == "SKY"):
            weather_code = item.get("fcstValue")

            if weather_code == '1':
                weather_state = '맑음'

            elif weather_code == '3':
                weather_state = '구름많음'

            else:
                weather_state = '흐림'

            tomorrow['날씨'] = weather_state

    tmp = int(tomorrow['기온'])
    sky = tomorrow['날씨']
    pty = tomorrow['눈/비 소식']
    pop = int(tomorrow['강수확률'])
    wsd = tomorrow['풍속']
    reh = tomorrow['습도']

    # tomorrow_result에 내일 출근 날씨 정보 

    tomorrow_result = []
    tomorrow_result.append(tmp)
    tomorrow_result.append(sky)
    tomorrow_result.append(pty)
    tomorrow_result.append(pop)
    tomorrow_result.append(wsd)
    tomorrow_result.append(reh)
    tomorrow_result.append(tomorrow_date)


    # print(base_date)
    # print(base_time)
    # print(res)
    
    # print(today)
    # print(tomorrow)

    
    # return HttpResponse(res)
    # weather.html로 보내 출력하기
    return render(request, 'home/weather.html', {'today': today_result, 'tomorrow':tomorrow_result})




################################## kakaotalk service
##################################
##################################


# Create your views here.

# def kakaologinhome(request):
#     return render(request, 'templates/kakaologinhome.html')

def kakaologin(request):
    _context = {'check':False}
    if request.session.get('access_token'):
        _context['check'] = True
    return render(request, 'home/kakaologinhome.html', _context)

def kakaoLoginLogic(request):
    _restApiKey = '5d03e24af9d6c95a6f526e3308d8879d' # 입력필요
    _redirectUrl = 'http://127.0.0.1:8000/home/kakaoLoginLogicRedirect'
    _url = f'https://kauth.kakao.com/oauth/authorize?client_id={_restApiKey}&redirect_uri={_redirectUrl}&response_type=code'
    return redirect(_url)

def kakaoLoginLogicRedirect(request):
    _qs = request.GET['code']
    _restApiKey = '5d03e24af9d6c95a6f526e3308d8879d' # 입력필요
    _redirect_uri = 'http://127.0.0.1:8000/home/kakaoLoginLogicRedirect'
    _url = f'https://kauth.kakao.com/oauth/token?grant_type=authorization_code&client_id={_restApiKey}&redirect_uri={_redirect_uri}&code={_qs}'
    _res = requests.post(_url)
    _result = _res.json()
    request.session['access_token'] = _result['access_token']
    request.session.modified = True
    return render(request, 'home/kakaologinSuccess.html')

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
        return render(request, 'home/kakaologoutSuccess.html')
    else:
        return render(request, 'home/kakaologoutError.html')

#날씨 요약 정보
def kakaoMessage_climate(request):
    cloth = ""

    if temperature <= 4:
        cloth = "패딩, 목도리, 장갑"
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
        cloth = "한여름 옷차림"

    if rain >= 60:
        cloth += ", 우산"

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
            "text": "오늘의 Weather & Gather\n" + "기온 : " + (str)(temperature) + "'C\n강수확률 : " + (str)(rain) + "%\n오늘은 " + cloth + " 추천드립니다.",
            "link":{
                "web_url":"http://127.0.0.1:8000/home/index"
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
    return render(request, 'home/kakaoMessageSent.html')