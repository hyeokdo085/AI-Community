# client_like.py
# 게시글 좋아요(Like) 및 좋아요 취소(Unlike)를 처리하는 클라이언트 모듈

import requests
import json

# 서버 기본 주소 설정
SERVER_BASE_URL = "http://127.0.0.1:5000"

def toggle_post_like_client(post_id, access_token):
    # 특정 게시글에 대한 좋아요 상태를 토글하는 함수
    # 좋아요/취소는 POST 요청으로 처리하며, 인증 토큰(JWT)이 필요

    # API 엔드포인트 URL 구성
    url = f"{SERVER_BASE_URL}/api/posts/{post_id}/like"
    
    # 요청 헤더에 JWT 토큰을 포함 (Bearer scheme 사용)
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    print(f"\n[CLIENT] 좋아요/취소 요청 시도: 게시글 ID {post_id}")
    try:
        # 서버에 POST 요청 전송 (좋아요/취소는 body 없이 헤더만으로 요청)
        response = requests.post(url, headers=headers)
        response_data = response.json()
        
        # 응답 출력
        print(f"[서버 응답] 상태 코드: {response.status_code}")
        print(f"[서버 응답] 내용:")
        print(json.dumps(response_data, indent=4, ensure_ascii=False))
        
        return response_data

    except requests.exceptions.ConnectionError:
        print("[오류] 서버에 연결할 수 없습니다. 서버가 실행 중인지 확인하세요.")
        return None
    except Exception as e:
        print(f"[오류] 예외 발생: {e}")
        return None
