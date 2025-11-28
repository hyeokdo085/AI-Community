# server_API.py
# 서버 API 모듈 (게시글, 댓글, 좋아요 관련 엔드포인트 정의)

# ---------------------------------모듈 영역--------------------------------------------
    
from flask import Flask, request, jsonify 
# Flask의 핵심 기능과 JSON 처리 기능

from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity 
# JWT 인증 관련 기능: 관리자(JWTManager), 토큰 생성(create_access_token), 
# 인증 요구(jwt_required), 사용자 ID 추출(get_jwt_identity)

from server_login_register import register_user, login_user 
# 로그인/회원가입 로직

from server_posts import create_post, get_all_posts, get_post_detail, update_post, delete_post
# 게시글 로직

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




# ----------------------------------------------------------------------------------------------
# 회원가입/로그인 API 엔드포인트
# ----------------------------------------------------------------------------------------------

# 1. 회원가입 (POST: /register)
@community_API.route('/register', methods=['POST'])
def api_register():
    # 요청 본문에서 이메일과 비밀번호 추출
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        # 필수 필드 누락 시 400 Bad Request
        return jsonify({"status": "FAILURE", "message": "이메일과 비밀번호를 입력해주세요."}), 400

    # DB 로직 호출
    result = register_user(email, password)
    
    if result["status"] == "SUCCESS":
        # 성공 시 201 Created
        return jsonify(result), 201
    else:
        # 이메일 중복 등 실패 시 409 Conflict 또는 500 Internal Server Error
        return jsonify(result), 409 if "이메일" in result["message"] else 500

# 2. 로그인 (POST: /login)
@community_API.route('/login', methods=['POST'])
def api_login():
    # 요청 본문에서 이메일과 비밀번호 추출
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    # DB 로직 호출
    result = login_user(email, password)
    
    if result["status"] == "SUCCESS":
        # 로그인 성공 시 사용자 ID를 이용해 JWT 액세스 토큰 생성
        user_id = result["user_id"]
        access_token = create_access_token(identity=user_id)
        
        # 토큰과 성공 메시지 반환 (200 OK)
        return jsonify({
            "status": "SUCCESS", 
            "message": "로그인 성공", 
            "user_id": user_id,
            "access_token": access_token
        }), 200
    else:
        # 로그인 실패 (비밀번호 불일치, 사용자 없음 등) 시 401 Unauthorized
        return jsonify(result), 401
    




# =======================================================================
# 게시글 API 엔드포인트
# =======================================================================

# 1. 게시글 목록 조회 (GET: /api/posts)
@community_API.route('/api/posts', methods=['GET'])
def api_get_all_posts():
    # DB 로직 호출 (권한 불필요)
    result = get_all_posts()
    
    if result["status"] == "SUCCESS":
        return jsonify(result), 200
    else:
        return jsonify(result), 500

# 2. 게시글 작성 (POST: /api/posts)
@community_API.route('/api/posts', methods=['POST'])
@jwt_required() # 인증된 사용자만 접근 가능
def api_create_post():
    # JWT 토큰에서 사용자 ID 추출 (게시글 작성자)
    user_id = int(get_jwt_identity())
    data = request.get_json()
    
    # 요청 본문에서 필드 추출
    title = data.get('title')
    body = data.get('body')
    # pinned와 private 필드 추출 (기본값 False)
    pinned = data.get('pinned', False) 
    private = data.get('private', False)

    if not title or not body:
        # 필수 필드 누락 시 400 Bad Request
        return jsonify({"status": "FAILURE", "message": "제목과 내용을 입력해주세요."}), 400

    # DB 로직 호출 (pinned, private 상태 전달)
    result = create_post(user_id, title, body, pinned, private)
    
    if result["status"] == "SUCCESS":
        # 성공 시 201 Created
        return jsonify(result), 201 
    else:
        return jsonify(result), 500

# 3. 게시글 상세 조회 (GET: /api/posts/<post_id>)
@community_API.route('/api/posts/<int:post_id>', methods=['GET'])
def api_get_post_detail(post_id):
    # JWT 토큰 유무와 관계없이 상세 조회가 가능해야 함
    # 비공개 게시글 처리를 위해, 토큰이 있다면 user_id를 추출하여 DB 로직에 전달해야 함.
    requested_user_id = None
    
    # TODO: Flask-JWT-Extended에서 @jwt_required(optional=True)를 사용하여
    # 요청자 ID (requested_user_id)를 추출하는 로직 구현 필요.
    # 현재는 요청자 ID 없이 호출한다고 가정하고, DB 로직이 권한 체크를 담당함.
    
    # DB 로직 호출
    result = get_post_detail(post_id, requested_user_id)
    
    if result["status"] == "SUCCESS":
        return jsonify(result), 200
    elif result["message"] == "비공개 게시글이거나, 접근 권한이 없습니다.":
        # 권한 없는 비공개 게시글 접근 시 403 Forbidden
        return jsonify(result), 403
    else:
        # 게시글을 찾을 수 없는 경우 404 Not Found
        return jsonify(result), 404

# 4. 게시글 수정 및 삭제 (PUT/DELETE: /api/posts/<post_id>)
@community_API.route('/api/posts/<int:post_id>', methods=['PUT', 'DELETE'])
@jwt_required() # 수정 및 삭제는 인증 필수
def api_update_delete_post(post_id):
    # JWT 토큰에서 사용자 ID 추출 (권한 확인용)
    user_id = int(get_jwt_identity())
    
    if request.method == 'PUT':
        # 4-A. 수정 로직
        data = request.get_json()
        title = data.get('title')
        body = data.get('body')
        # pinned와 private 필드 추출
        pinned = data.get('pinned') 
        private = data.get('private')
        
        # 필수 필드 검사
        if not title or not body or pinned is None or private is None:
            return jsonify({"status": "FAILURE", "message": "제목, 내용, 고정 상태, 비공개 상태를 모두 입력해주세요."}), 400
            
        # DB 로직 호출 (작성자 ID와 일치하는지 확인)
        result = update_post(post_id, user_id, title, body, pinned, private)
        
    elif request.method == 'DELETE':
        # 4-B. 삭제 로직
        # DB 로직 호출 (작성자 ID와 일치하는지 확인)
        result = delete_post(post_id, user_id)
        
    # 결과 응답 처리
    if result["status"] == "SUCCESS":
        return jsonify(result), 200
    elif result["message"] == "권한 없음":
        # 게시글 작성자가 아닌 경우 403 Forbidden
        return jsonify(result), 403 
    else:
        # 게시글 ID를 찾을 수 없는 경우 404 Not Found
        return jsonify(result), 404





# =======================================================================
# 댓글 API 엔드포인트
# =======================================================================

# 1. 댓글 생성 (POST: /api/posts/<post_id>/comments)
@community_API.route('/api/posts/<int:post_id>/comments', methods=['POST'])
@jwt_required() # 댓글 작성은 인증 필수
def api_create_comment(post_id):
    # JWT 토큰에서 사용자 ID 추출
    user_id = int(get_jwt_identity())
    data = request.get_json()
    comment_body = data.get('body')
    
    if not comment_body:
        return jsonify({"status": "FAILURE", "message": "댓글 내용을 입력해주세요."}), 400
        
    # DB 로직 호출
    result = create_comment(post_id, user_id, comment_body)
    
    if result["status"] == "SUCCESS":
        # 성공 시 201 Created
        return jsonify(result), 201
    else:
        return jsonify(result), 500

# 2. 댓글 목록 조회 (GET: /api/posts/<post_id>/comments)
@community_API.route('/api/posts/<int:post_id>/comments', methods=['GET'])
def api_get_comments(post_id):
    # DB 로직 호출 (인증 불필요)
    result = get_comments_by_post(post_id)
    
    if result["status"] == "SUCCESS":
        return jsonify(result), 200
    else:
        # 게시글 ID를 찾을 수 없는 경우 404 Not Found
        return jsonify(result), 404
    
# 3. 댓글 수정 및 삭제 (PUT/DELETE: /api/comments/<comment_id>)
@community_API.route('/api/comments/<int:comment_id>', methods=['PUT', 'DELETE'])
@jwt_required() # 수정 및 삭제는 인증 필수
def api_update_delete_comment(comment_id):
    # JWT 토큰에서 사용자 ID 추출 (권한 확인용)
    user_id = int(get_jwt_identity())
    
    if request.method == 'PUT':
        # PUT (수정) 요청 처리
        data = request.get_json()
        new_body = data.get('body')
        
        if not new_body:
            return jsonify({"status": "FAILURE", "message": "수정할 댓글 내용을 입력해주세요."}), 400
            
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
    
    if result["status"] == "SUCCESS":
        # 성공 시 200 OK
        return jsonify(result), 200
    else:
        # DB 연결 오류 등 실패 시 500 Internal Server Error
        return jsonify(result), 500