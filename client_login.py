# client_login.py
# 로그인 클라이언트 모듈

import requests
import json

# 서버 기본 주소 설정
SERVER_BASE_URL = "http://127.0.0.1:5000"
# socket 헤더가 없어도 requests, flask가 자동으로 설정해줌

# 로그인 요청 함수
def login_client(email, password):
    
    # POST 요청에 보낼 JSON 데이터 구성
    url = f"{SERVER_BASE_URL}/login"
    payload = {
        "email": email,
        "password": password
    }
    
    print(f"\n[CLIENT] 로그인 요청 시도: {email}")
    try:
        response = requests.post(url, json=payload)
        response_data = response.json()
        
        print(f"[서버 응답] 상태 코드: {response.status_code}")
        print(f"[서버 응답] 내용:")
        print(json.dumps(response_data, indent=4, ensure_ascii=False))
        
    except requests.exceptions.ConnectionError:
        print("[오류] 서버에 연결할 수 없습니다. 서버가 실행 중인지 확인하세요.")
    except Exception as e:
        print(f"[오류] 예외 발생: {e}")