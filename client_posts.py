# client_posts.py
# 게시글 관련 API를 호출하는 클라이언트 측 로직

import requests
import json

# 서버 기본 주소 설정
SERVER_BASE_URL = "http://127.0.0.1:5000"

# -------------------------- 1. 게시글 생성 (Create) --------------------------
# post_data: {title: str, body: str, pinned: bool, private: bool}
# access_token: JWT 인증 토큰
def create_post_client(post_data, access_token):
    # API 엔드포인트 URL
    url = f"{SERVER_BASE_URL}/api/posts"
    
    # 요청 헤더에 JWT 토큰을 포함
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    print(f"\n[CLIENT] 게시글 작성 요청 시도: 제목 '{post_data.get('title')}' (비공개: {post_data.get('private', False)})")
    try:
        # 서버에 POST 요청 전송
        response = requests.post(url, headers=headers, json=post_data)
        # 응답 데이터 파싱
        response_data = response.json()
        
        print(f"[서버 응답] 상태 코드: {response.status_code}")
        print(f"[서버 응답] 내용:")
        print(json.dumps(response_data, indent=4, ensure_ascii=False))
        
        # 성공 시 응답 데이터 반환
        if response.status_code == 201:
            return response_data
        
    except requests.exceptions.ConnectionError:
        print("[오류] 서버에 연결할 수 없습니다. 서버가 실행 중인지 확인하세요.")
    except requests.exceptions.JSONDecodeError:
        print(f"[오류] 게시글 작성 요청 중 예외 발생: 응답이 JSON 형식이 아님. 상태 코드: {response.status_code}")
    except Exception as e:
        print(f"[오류] 게시글 작성 요청 중 예외 발생: {e}")
    
    return None

# -------------------------- 2. 게시글 목록 조회 (Read - List) --------------------------
# 공개 게시글 전체 목록을 조회
def get_all_posts_client():
    # API 엔드포인트 URL
    url = f"{SERVER_BASE_URL}/api/posts"
    
    print("\n[CLIENT] 게시글 전체 목록 조회 요청 시도")
    try:
        # 서버에 GET 요청 전송 (인증 불필요)
        response = requests.get(url)
        response_data = response.json()
        
        print(f"[서버 응답] 상태 코드: {response.status_code}")
        # 목록 데이터가 크므로 응답 내용은 생략하고 요약 정보만 출력
        print(f"[서버 응답] 내용: 게시글 {response_data.get('total_posts', 0)}개 조회")
        
        # 성공 시 응답 데이터 반환
        if response.status_code == 200:
            return response_data
            
    except requests.exceptions.ConnectionError:
        print("[오류] 서버에 연결할 수 없습니다. 서버가 실행 중인지 확인하세요.")
    except Exception as e:
        print(f"[오류] 게시글 목록 조회 요청 중 예외 발생: {e}")
        
    return None

# -------------------------- 3. 게시글 상세 조회 (Read - Detail) --------------------------
# post_id: 조회할 게시글 ID
def get_post_detail_client(post_id, access_token=None):
    # API 엔드포인트 URL
    url = f"{SERVER_BASE_URL}/api/posts/{post_id}"
    
    headers = {}
    if access_token:
        # 비공개 게시글 조회를 위해 토큰이 있다면 헤더에 추가
        headers["Authorization"] = f"Bearer {access_token}"

    print(f"\n[CLIENT] 게시글 상세 조회 요청 시도: ID {post_id}")
    try:
        # 서버에 GET 요청 전송
        response = requests.get(url, headers=headers)
        response_data = response.json()
        
        print(f"[서버 응답] 상태 코드: {response.status_code}")
        print(f"[서버 응답] 내용:")
        print(json.dumps(response_data, indent=4, ensure_ascii=False))
        
        # 성공 시 응답 데이터 반환
        if response.status_code == 200:
            return response_data
            
    except requests.exceptions.ConnectionError:
        print("[오류] 서버에 연결할 수 없습니다. 서버가 실행 중인지 확인하세요.")
    except requests.exceptions.JSONDecodeError:
        print(f"[오류] 게시글 상세 조회 요청 중 예외 발생: 응답이 JSON 형식이 아님. 상태 코드: {response.status_code}")
    except Exception as e:
        print(f"[오류] 게시글 상세 조회 요청 중 예외 발생: {e}")
        
    return None

# -------------------------- 4. 게시글 수정 (Update) --------------------------
# post_id: 수정할 게시글 ID
# update_data: {title: str, body: str, pinned: bool, private: bool}
# access_token: JWT 인증 토큰 (권한 확인용)
def update_post_client(post_id, update_data, access_token):
    # API 엔드포인트 URL
    url = f"{SERVER_BASE_URL}/api/posts/{post_id}"
    
    # 요청 헤더에 JWT 토큰을 포함
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    print(f"\n[CLIENT] 게시글 수정 요청 시도: ID {post_id}, 제목 '{update_data.get('title')}'")
    try:
        # 서버에 PUT 요청 전송
        response = requests.put(url, headers=headers, json=update_data)
        response_data = response.json()
        
        print(f"[서버 응답] 상태 코드: {response.status_code}")
        print(f"[서버 응답] 내용:")
        print(json.dumps(response_data, indent=4, ensure_ascii=False))
        
        # 성공 시 응답 데이터 반환
        if response.status_code == 200:
            return response_data
        
    except requests.exceptions.ConnectionError:
        print("[오류] 서버에 연결할 수 없습니다. 서버가 실행 중인지 확인하세요.")
    except requests.exceptions.JSONDecodeError:
        print(f"[오류] 게시글 수정 요청 중 예외 발생: 응답이 JSON 형식이 아님. 상태 코드: {response.status_code}")
    except Exception as e:
        print(f"[오류] 게시글 수정 요청 중 예외 발생: {e}")
        
    return None

# -------------------------- 5. 게시글 삭제 (Delete) --------------------------
# post_id: 삭제할 게시글 ID
# access_token: JWT 인증 토큰 (권한 확인용)
def delete_post_client(post_id, access_token):
    # API 엔드포인트 URL
    url = f"{SERVER_BASE_URL}/api/posts/{post_id}"
    
    # 요청 헤더에 JWT 토큰을 포함
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    print(f"\n[CLIENT] 게시글 삭제 요청 시도: ID {post_id}")
    try:
        # 서버에 DELETE 요청 전송
        response = requests.delete(url, headers=headers)
        # 삭제는 응답 본문이 없을 수 있으므로, 상태 코드만 확인
        
        # 서버 응답이 있을 경우 JSON 파싱 시도 (403, 404 등 실패 응답)
        if response.content:
            response_data = response.json()
            print(f"[서버 응답] 상태 코드: {response.status_code}")
            print(f"[서버 응답] 내용:")
            print(json.dumps(response_data, indent=4, ensure_ascii=False))
        else:
            response_data = {"status": "SUCCESS", "message": "게시글이 성공적으로 삭제되었습니다."}
            print(f"[서버 응답] 상태 코드: {response.status_code}")
            print(f"[서버 응답] 내용: 삭제 성공")


        # 성공 (200 OK) 또는 기타 응답 코드를 확인
        if response.status_code == 200:
            return response_data
            
    except requests.exceptions.ConnectionError:
        print("[오류] 서버에 연결할 수 없습니다. 서버가 실행 중인지 확인하세요.")
    except requests.exceptions.JSONDecodeError:
        # 삭제 성공 시 내용이 비어있어 JSONDecodeError가 발생할 수 있음
        if response.status_code == 200:
             return {"status": "SUCCESS", "message": "게시글이 성공적으로 삭제되었습니다."}
        print(f"[오류] 게시글 삭제 요청 중 예외 발생: 응답이 JSON 형식이 아님. 상태 코드: {response.status_code}")
    except Exception as e:
        print(f"[오류] 게시글 삭제 요청 중 예외 발생: {e}")
        
    return None