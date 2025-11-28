# server_API.py
# # 서버 API 모듈



# ---------------------------------모듈 영역--------------------------------------------
    
from flask import Flask, request, jsonify 
# Flask의 핵심 기능과 JSON 처리 기능

from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity 
# JWT 인증 관련 기능: 관리자(JWTManager), 토큰 생성(create_access_token), 
# 인증 요구(jwt_required), 사용자 ID 추출(get_jwt_identity)

from server_login_register import register_user, login_user 
# 로그인/회원가입 로직

from server_comment import create_comment, get_comments_by_post, update_comment, delete_comment
# 댓글 관리 로직

from server_like import toggle_post_like 
# 좋아요 관리 로직

# ----------------------------------------------------------------------------------------------



# Flask 애플리케이션 초기화
community_API = Flask(__name__)

# -------------------------- JWT 설정 --------------------------
# JWT 토큰 암호화 및 복호화에 사용되는 비밀 키 설정 (매우 중요)
# 실제 프로젝트에서는 환경 변수 등을 통해 관리
community_API.config["JWT_SECRET_KEY"] = "your_super_secret_jwt_key_for_project" 
jwt = JWTManager(community_API)

# JWT 에러 핸들링: 토큰이 누락되거나 유효하지 않을 때 (HTTP 401 Unauthorized 발생 시)
@jwt.unauthorized_loader
def unauthorized_callback(callback):
    # 클라이언트에게 401 Unauthorized 상태 코드와 함께 오류 메시지 반환
    return jsonify({
        "status": "FAILURE",
        "message": "인증 토큰이 누락되었거나 유효하지 않습니다."
    }), 401
# ----------------------------------------------------------------------



# =======================================================================
# 회원가입 및 로그인 API
# =======================================================================

# 회원가입 API 엔드포인트 구현: /register (POST 요청)
@community_API.route('/register', methods=['POST'])
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

    # 2. DB 로직 실행 (사용자 등록)
    result = register_user(email, password)

    # 3. 결과를 JSON 응답으로 반환
    if result["status"] == "SUCCESS":
        # 회원가입 성공 시 201 Created 상태 코드 반환 (REST API 표준)
        return jsonify(result), 201 
    else:
        # 이메일 중복 등 실패 시 409 Conflict 상태 코드 반환
        return jsonify(result), 409 


# 로그인 API 엔드포인트 구현: /login (POST 요청)
@community_API.route('/login', methods=['POST'])
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
        
    # 2. DB 로직 실행 (사용자 인증 및 user_id 획득)
    result = login_user(email, password)

    # 3. 결과를 JSON 응답으로 반환
    if result["status"] == "SUCCESS":
        # JWT subject(identity)에 user_id를 담아 인증 정보로 사용
        access_token = create_access_token(identity=str(result["user_id"]))
        
        result["access_token"] = access_token
        result["message"] = "로그인 성공 및 토큰 발급"
        
        # 로그인 성공 시 200 OK 상태 코드 반환 (토큰 포함)
        return jsonify(result), 200
    else:
        # 인증 실패 시 401 Unauthorized 상태 코드 반환
        return jsonify(result), 401 



# =======================================================================
# 댓글 API 엔드포인트
# =======================================================================

# 1. 댓글 생성 (POST: /api/posts/<post_id>/comments)
@community_API.route('/api/posts/<int:post_id>/comments', methods=['POST'])
@jwt_required() # 이 엔드포인트에 접근하려면 유효한 JWT 토큰이 필수
def api_create_comment(post_id):
    # JWT에서 인증된 사용자 ID(문자열 형태)를 추출하고 DB 사용을 위해 정수형으로 변환
    user_id = int(get_jwt_identity()) 
   
    data = request.get_json()
    comment_body = data.get('body')
    if not comment_body:
        return jsonify({"status": "FAILURE", "message": "댓글 내용이 누락되었습니다."}), 400

    # 댓글 DB 저장 로직 실행
    result = create_comment(post_id, user_id, comment_body)

    if result["status"] == "SUCCESS":
        return jsonify(result), 201 # 201 Created 응답
    else:
        # DB 오류 등 서버 문제 시 500 Internal Server Error
        return jsonify(result), 500

# 2. 댓글 목록 조회 (GET: /api/posts/<post_id>/comments)
@community_API.route('/api/posts/<int:post_id>/comments', methods=['GET'])
def api_get_comments(post_id):
    # 특정 게시글의 댓글 목록 조회 로직 실행 (인증 불필요)
    result = get_comments_by_post(post_id)
        
    if result["status"] == "SUCCESS":
        return jsonify(result), 200 # 200 OK 응답
    else:
        # 댓글이 없거나 게시글 ID가 잘못된 경우 404 Not Found 응답
        return jsonify(result), 404

# 3. 댓글 수정 및 삭제 (PUT/DELETE: /api/comments/<comment_id>)
@community_API.route('/api/comments/<int:comment_id>', methods=['PUT', 'DELETE'])
@jwt_required() # 수정/삭제는 토큰(인증) 필수
def api_handle_comment(comment_id):
    # JWT에서 사용자 ID를 추출하고 정수형으로 변환
    user_id = int(get_jwt_identity()) 

    if request.method == 'PUT':
        # PUT (수정) 요청 처리
        data = request.get_json()
        new_body = data.get('body')
            
        if not new_body:
            return jsonify({"status": "FAILURE", "message": "수정할 내용이 누락되었습니다."}), 400

        # 댓글 수정 로직 실행 (작성자 ID와 일치하는지 확인)
        result = update_comment(comment_id, user_id, new_body)
        
    elif request.method == 'DELETE':
        # DELETE (삭제) 요청 처리
        # 댓글 삭제 로직 실행 (작성자 ID와 일치하는지 확인)
        result = delete_comment(comment_id, user_id)
            
    # 결과 응답 처리
    if result["status"] == "SUCCESS":
        return jsonify(result), 200
    elif result["message"] == "권한 없음":
        # 댓글 작성자가 아닌 경우 403 Forbidden 응답
        return jsonify(result), 403 
    else:
        # 댓글 ID를 찾을 수 없는 경우 404 Not Found 응답
        return jsonify(result), 404
    


# =======================================================================
# 좋아요 API 엔드포인트
# =======================================================================
    # 게시글 좋아요 토글 (POST: /api/posts/<post_id>/like)
@community_API.route('/api/posts/<int:post_id>/like', methods=['POST'])
@jwt_required() # 좋아요 토글은 인증 필수
def api_toggle_like(post_id):
    # 1. JWT 토큰에서 사용자 ID 추출
    user_id = int(get_jwt_identity())

    # 2. 좋아요 로직 실행
    # toggle_post_like 함수가 LIKE 또는 UNLIKE 액션을 처리
    result = toggle_post_like(post_id, user_id)

    # 3. 결과 반환
    if result["status"] == "SUCCESS":
        # 좋아요 성공 또는 취소 성공 시 200 OK 응답
        return jsonify(result), 200
    elif "DB 처리 중 오류" in result["message"]:
        # DB 트랜잭션 오류 등 서버 내부 오류 발생 시 500 Internal Server Error
        return jsonify(result), 500
    else:
        # 기타 로직 오류 (예: post_id가 잘못된 경우 등)
        return jsonify(result), 404