# server_API.py
# 서버 API 모듈

from flask import Flask, request, jsonify 
# Flask의 핵심 기능과 JSON 처리 기능

from server_login_register import register_user, login_user 
# 로그인/회원가입 로직



# Flask 애플리케이션 초기화
community_API = Flask(__name__)

# 회원가입 API 엔드포인트 구현: /register (POST 요청)
@community_API.route('/register', methods=['POST']) # 회원가입 엔드포인트
def register():
    # 1. 클라이언트가 보낸 JSON 데이터(email, password) 받기
    data = request.get_json() # 클라이언트가 보낸 JSON 데이터 파싱
    email = data.get('email') # 이메일
    password = data.get('password') # 비밀번호

    # 필수 데이터 누락 확인
    if not email or not password:
        return jsonify({ # 필수 데이터 누락 시 오류 응답
            "status": "FAILURE", 
            "message": "이메일 또는 비밀번호가 누락되었습니다."
        }), 400 # 400 Bad Request HTTP 상태 코드 반환

    # 2. login_register.py의 함수를 호출하여 DB 처리 및 로직 실행
    result = register_user(email, password)

    # 3. 결과를 JSON 응답으로 반환
    if result["status"] == "SUCCESS":
        # 회원가입 성공 시 201 Created 상태 코드 반환 (REST API 표준)
        return jsonify(result), 201 
    else:
        # 실패 시 409 Conflict 또는 500 Internal Server Error 상태 코드 반환
        return jsonify(result), 409 


# 로그인 API 엔드포인트 구현: /login (POST 요청)
@community_API.route('/login', methods=['POST']) # 로그인 엔드포인트
def login():
    # 1. 클라이언트가 보낸 JSON 데이터 받기
    data = request.get_json()
    email = data.get('email') 
    password = data.get('password')

    if not email or not password:
        return jsonify({ 
            "status": "FAILURE", 
            "message": "이메일 또는 비밀번호가 누락되었습니다." 
        }), 400
    
    # 2. login_register.py의 함수를 호출하여 DB 처리 및 로직 실행
    result = login_user(email, password)

    # 3. 결과를 JSON 응답으로 반환
    if result["status"] == "SUCCESS":
        # 로그인 성공 시 200 OK 상태 코드 반환
        return jsonify(result), 200
    else:
        # 로그인 실패 시 401 Unauthorized 상태 코드 반환 (인증 실패)
        return jsonify(result), 401 