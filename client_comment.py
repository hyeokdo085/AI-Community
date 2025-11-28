# client_comment.py
# 댓글 기능을 위한 클라이언트 모듈

import requests
import json

# 서버 기본 주소 설정
SERVER_BASE_URL = "http://127.0.0.1:5000"

def create_comment_client(post_id, access_token, body):
    # 댓글 생성 API 호출
    url = f"{SERVER_BASE_URL}/api/posts/{post_id}/comments"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    payload = {"body": body}
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        return response.json()
    except Exception as e:
        print(f"[오류] 댓글 생성 요청 중 예외 발생: {e}")
        return None

def get_comments_client(post_id):
    # 댓글 목록 조회 API 호출 (인증 불필요)
    url = f"{SERVER_BASE_URL}/api/posts/{post_id}/comments"
    
    try:
        response = requests.get(url)
        return response.json()
    except Exception as e:
        print(f"[오류] 댓글 조회 요청 중 예외 발생: {e}")
        return None
        
def update_comment_client(comment_id, access_token, new_body):
    # 댓글 수정 API 호출
    url = f"{SERVER_BASE_URL}/api/comments/{comment_id}"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    payload = {"body": new_body}
    
    try:
        response = requests.put(url, headers=headers, json=payload)
        return response.json()
    except Exception as e:
        print(f"[오류] 댓글 수정 요청 중 예외 발생: {e}")
        return None

def delete_comment_client(comment_id, access_token):
    # 댓글 삭제 API 호출
    url = f"{SERVER_BASE_URL}/api/comments/{comment_id}"
    headers = {
        "Authorization": f"Bearer {access_token}",
    }
    
    try:
        response = requests.delete(url, headers=headers)
        return response.json()
    except Exception as e:
        print(f"[오류] 댓글 삭제 요청 중 예외 발생: {e}")
        return None