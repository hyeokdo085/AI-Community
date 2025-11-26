# client_register.py
# 회원가입 클라이언트 모듈

import requests
import json

# 서버 기본 주소 설정
SERVER_BASE_URL = "http://127.0.0.1:5000"
# socket 헤더가 없어도 requests, flask가 자동으로 설정해줌

# 회원가입 요청 함수
def register_client(email, password):
    """Sends a registration request to the server."""
    
    url = f"{SERVER_BASE_URL}/register"
    # POST 요청에 보낼 JSON 데이터 구성
    payload = {
        "email": email,
        "password": password
    }
    
    print(f"\n[CLIENT] 회원가입 요청 시도: {email}")
    try:
        # 서버에 POST 요청 전송
        response = requests.post(url, json=payload)
        
        # 서버 응답 JSON 데이터 파싱
        response_data = response.json()

        # 응답 출력
        print(f"[서버 응답] 상태 코드: {response.status_code}")
        print(f"[서버 응답] 내용:")
        print(json.dumps(response_data, indent=4, ensure_ascii=False))

    except requests.exceptions.ConnectionError:
        print("[오류] 서버에 연결할 수 없습니다. 서버가 실행 중인지 확인하세요.")
    except Exception as e:
        print(f"[오류] 예외 발생: {e}")