# server_API.py
# 서버 API 모듈

import os
from collections import deque

from flask import (
    Flask,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from ai_service import ai_service
from chat_protocol import ProtocolError, build_packet, validate_packet
from server_login_register import login_user, register_user
from server_comment import create_comment, get_comments_by_post, update_comment, delete_comment
from server_posts import create_post, get_posts, get_post, update_post, delete_post
from server_like import toggle_like, get_like_count, check_user_liked

# Flask 애플리케이션 초기화
community_API = Flask(__name__)
community_API.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret")
community_API.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
)

chat_history = deque(maxlen=200)


def _require_login():
    if "user" not in session:
        return None
    return session["user"]


@community_API.route("/")
def index():
    if "user" in session:
        return redirect(url_for("community_page"))
    return render_template("index.html")


@community_API.route("/community")
def community_page():
    user = _require_login()
    if not user:
        return redirect(url_for("index"))
    return render_template("community.html", user=user)


@community_API.route("/chat")
def chat_room():
    user = _require_login()
    if not user:
        return redirect(url_for("index"))
    return render_template("chat.html", user=user)


@community_API.route("/logout", methods=["POST"])
def logout():
    session.clear()
    if request.accept_mimetypes.accept_json:
        return jsonify({"status": "SUCCESS", "message": "로그아웃 되었습니다."})
    return redirect(url_for("index"))


@community_API.route("/session", methods=["GET"])
def session_state():
    user = session.get("user")
    if not user:
        return jsonify({"authenticated": False})
    return jsonify({"authenticated": True, "user": user})

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
        session["user"] = {"id": result["user_id"], "email": email}
        return jsonify(result), 200
    else:
        # 로그인 실패 시 401 Unauthorized 상태 코드 반환 (인증 실패)
        return jsonify(result), 401 


@community_API.route("/api/chat/history", methods=["GET"])
def get_chat_history():
    user = _require_login()
    if not user:
        return jsonify({"status": "FAILURE", "message": "로그인이 필요합니다."}), 401
    return jsonify({"status": "SUCCESS", "history": list(chat_history)})


@community_API.route("/api/chat/send", methods=["POST"])
def send_chat():
    user = _require_login()
    if not user:
        return jsonify({"status": "FAILURE", "message": "로그인이 필요합니다."}), 401

    data = request.get_json() or {}
    packet = data.get("packet")
    if not packet:
        return jsonify({"status": "FAILURE", "message": "packet 필드가 필요합니다."}), 400

    try:
        normalized = validate_packet(packet)
    except ProtocolError as exc:
        return jsonify({"status": "FAILURE", "message": str(exc)}), 400

    # 보안을 위해 서버 측 정보를 강제로 덮어씀
    normalized["header"]["sender"] = user["email"]
    normalized["payload"]["metadata"]["user_id"] = user["id"]
    chat_history.append(normalized)

    ai_packet = None
    if data.get("ask_ai", True):
        ai_text = ai_service.reply(
            [item["payload"]["body"] for item in chat_history if item["header"]["message_type"] == "CHAT"],
            normalized["payload"]["body"],
        )
        ai_packet = build_packet(
            sender="AI-Community",
            body=ai_text,
            message_type="AI",
            channel=normalized["header"]["channel"],
            metadata={"source": "openai" if ai_service.available else "fallback"},
        )
        chat_history.append(ai_packet)

    return jsonify(
        {
            "status": "SUCCESS",
            "packet": normalized,
            "ai_packet": ai_packet,
        }
    )


# ==================== 댓글 API 엔드포인트 ====================

@community_API.route("/api/comments/create", methods=["POST"])
def api_create_comment():
    user = _require_login()
    if not user:
        return jsonify({"status": "FAILURE", "message": "로그인이 필요합니다."}), 401
    
    data = request.get_json() or {}
    post_id = data.get("post_id")
    comment_body = data.get("comment_body")
    
    if not post_id or not comment_body:
        return jsonify({"status": "FAILURE", "message": "post_id와 comment_body가 필요합니다."}), 400
    
    result = create_comment(post_id, user["id"], comment_body)
    return jsonify(result), 201 if result["status"] == "SUCCESS" else 400


@community_API.route("/api/comments/<int:post_id>", methods=["GET"])
def api_get_comments(post_id):
    result = get_comments_by_post(post_id)
    # 댓글이 없어도 200 반환 (SUCCESS with empty array)
    return jsonify(result), 200


@community_API.route("/api/comments/update", methods=["PUT"])
def api_update_comment():
    user = _require_login()
    if not user:
        return jsonify({"status": "FAILURE", "message": "로그인이 필요합니다."}), 401
    
    data = request.get_json() or {}
    comment_id = data.get("comment_id")
    new_body = data.get("comment_body")
    
    if not comment_id or not new_body:
        return jsonify({"status": "FAILURE", "message": "comment_id와 comment_body가 필요합니다."}), 400
    
    result = update_comment(comment_id, user["id"], new_body)
    return jsonify(result), 200 if result["status"] == "SUCCESS" else 403


@community_API.route("/api/comments/delete/<int:comment_id>", methods=["DELETE"])
def api_delete_comment(comment_id):
    user = _require_login()
    if not user:
        return jsonify({"status": "FAILURE", "message": "로그인이 필요합니다."}), 401
    
    result = delete_comment(comment_id, user["id"])
    return jsonify(result), 200 if result["status"] == "SUCCESS" else 403


# ==================== 게시글 API 엔드포인트 ====================

@community_API.route("/api/posts", methods=["GET"])
def api_get_posts():
    result = get_posts()
    if result["status"] == "SUCCESS" and "posts" in result:
        # 각 게시글에 사용자가 좋아요했는지 정보 추가
        user = _require_login()
        if user:
            for post in result["posts"]:
                post["is_author"] = (post["user_id"] == user["id"])
                like_result = check_user_liked(post["post_id"], user["id"])
                post["user_liked"] = like_result.get("liked", False)
    return jsonify(result), 200


@community_API.route("/api/posts/<int:post_id>", methods=["GET"])
def api_get_post(post_id):
    result = get_post(post_id)
    if result["status"] == "SUCCESS" and "post" in result:
        user = _require_login()
        if user:
            result["post"]["is_author"] = (result["post"]["user_id"] == user["id"])
            like_result = check_user_liked(post_id, user["id"])
            result["post"]["user_liked"] = like_result.get("liked", False)
    return jsonify(result), 200 if result["status"] == "SUCCESS" else 404


@community_API.route("/api/posts/create", methods=["POST"])
def api_create_post():
    user = _require_login()
    if not user:
        return jsonify({"status": "FAILURE", "message": "로그인이 필요합니다."}), 401
    
    data = request.get_json() or {}
    title = data.get("title")
    content = data.get("content")
    
    if not title or not content:
        return jsonify({"status": "FAILURE", "message": "제목과 내용이 필요합니다."}), 400
    
    result = create_post(user["id"], title, content)
    return jsonify(result), 201 if result["status"] == "SUCCESS" else 400


@community_API.route("/api/posts/update", methods=["PUT"])
def api_update_post():
    user = _require_login()
    if not user:
        return jsonify({"status": "FAILURE", "message": "로그인이 필요합니다."}), 401
    
    data = request.get_json() or {}
    post_id = data.get("post_id")
    title = data.get("title")
    content = data.get("content")
    
    if not post_id or not title or not content:
        return jsonify({"status": "FAILURE", "message": "post_id, 제목, 내용이 필요합니다."}), 400
    
    result = update_post(post_id, user["id"], title, content)
    return jsonify(result), 200 if result["status"] == "SUCCESS" else 403


@community_API.route("/api/posts/delete/<int:post_id>", methods=["DELETE"])
def api_delete_post(post_id):
    user = _require_login()
    if not user:
        return jsonify({"status": "FAILURE", "message": "로그인이 필요합니다."}), 401
    
    result = delete_post(post_id, user["id"])
    return jsonify(result), 200 if result["status"] == "SUCCESS" else 403


# ==================== 좋아요 API 엔드포인트 ====================

@community_API.route("/api/likes/toggle", methods=["POST"])
def api_toggle_like():
    user = _require_login()
    if not user:
        return jsonify({"status": "FAILURE", "message": "로그인이 필요합니다."}), 401
    
    data = request.get_json() or {}
    post_id = data.get("post_id")
    
    if not post_id:
        return jsonify({"status": "FAILURE", "message": "post_id가 필요합니다."}), 400
    
    result = toggle_like(post_id, user["id"])
    return jsonify(result), 200 if result["status"] == "SUCCESS" else 400


@community_API.route("/api/likes/<int:post_id>", methods=["GET"])
def api_get_like_count(post_id):
    result = get_like_count(post_id)
    return jsonify(result), 200