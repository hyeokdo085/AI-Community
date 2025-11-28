# client_comment.py
# 댓글 API 호출 클라이언트 모듈 (JWT 사용)

import requests
import json
import time # 댓글 생성 후 목록 조회까지 시간차를 두기 위해 추가 (선택 사항)

SERVER_BASE_URL = "http://127.0.0.1:5000"

def call_api(method, url, token=None, json_data=None):
    # API 요청 생성 및 전송
    headers = {}
    if token:
        # JWT 토큰을 Authorization 헤더에 Bearer 형식으로 추가
        headers['Authorization'] = f'Bearer {token}'
    
    print(f"\n[CLIENT] {method} 요청 시도: {url}")
    try:
        response = requests.request(method, f"{SERVER_BASE_URL}{url}", headers=headers, json=json_data)
        response_data = response.json()
        
        print(f"[서버 응답] 상태 코드: {response.status_code}")
        print(f"[서버 응답] 내용:")
        print(json.dumps(response_data, indent=4, ensure_ascii=False))
        
        return response.status_code, response_data
        
    except requests.exceptions.ConnectionError:
        print("[오류] 서버에 연결할 수 없습니다. 서버가 실행 중인지 확인하세요.")
        return 500, None
    except Exception as e:
        print(f"[오류] 예외 발생: {e}")
        return 500, None

# -------------------------- 댓글 테스트 메인 함수 --------------------------

if __name__ == '__main__':
    TEST_EMAIL = "test_client123@test.com"
    TEST_PASSWORD = "testpass222@"
    
    # 테스트 전, 이메일로 가입된 사용자(`server_login_register.py` 테스트 실행)와 
    # 최소한 하나의 게시글(post_id=1)이 DB에 존재해야 합니다.
    TEST_POST_ID = 1 
    TEST_COMMENT_ID = None # 실제 생성된 ID를 저장할 변수

    # 1. 로그인하여 토큰 획득
    print("--- 1. 로그인하여 JWT 토큰 획득 ---")
    login_url = "/login"
    login_payload = {"email": TEST_EMAIL, "password": TEST_PASSWORD}
    status, data = call_api('POST', login_url, json_data=login_payload)
    
    if status != 200 or 'access_token' not in data:
        print("로그인 실패. 테스트를 중단합니다.")
        exit()
        
    auth_token = data['access_token']
    print(f"획득한 토큰: {auth_token[:20]}...")

    # 2. 댓글 생성 테스트 (POST)
    print("\n--- 2. 댓글 생성 테스트 (POST) ---")
    comment_create_url = f"/api/posts/{TEST_POST_ID}/comments"
    comment_payload = {"body": "첫 번째 테스트 댓글입니다."}
    create_status, create_data = call_api('POST', comment_create_url, token=auth_token, json_data=comment_payload)

    # 생성된 댓글 ID를 응답에서 추출
    if create_status == 201 and 'comment_id' in create_data:
        TEST_COMMENT_ID = create_data['comment_id']
        print(f"[SUCCESS] 새로 생성된 댓글 ID: {TEST_COMMENT_ID} 추출 완료.")
    elif create_status == 201:
        # 서버에서 ID를 바로 주지 않을 경우, 목록 조회에서 ID를 얻어와야 함
        print("[WARNING] POST 응답에 comment_id가 없습니다. 3단계에서 ID를 추출합니다.")
        time.sleep(1) # 서버 처리를 기다림 (선택 사항)
    else:
        print("댓글 생성 실패. 테스트를 중단합니다.")
        exit()


    # 3. 댓글 목록 조회 테스트 (GET)
    print("\n--- 3. 댓글 목록 조회 테스트 (GET) ---")
    list_status, list_data = call_api('GET', comment_create_url)
    
    # 목록에서 ID 추출 (POST 응답에 ID가 없었을 경우)
    if TEST_COMMENT_ID is None and list_status == 200 and list_data.get('comments'):
        TEST_COMMENT_ID = list_data['comments'][0]['comment_id']
        print(f"[SUCCESS] 목록 조회에서 댓글 ID: {TEST_COMMENT_ID} 추출 완료.")

    if TEST_COMMENT_ID is None:
        print("댓글 ID를 확보하지 못했습니다. 수정/삭제 테스트를 건너뜁니다.")
        exit()

    # 4. 댓글 수정 테스트 (PUT)
    print(f"\n--- 4. 댓글 수정 테스트 (PUT) - ID: {TEST_COMMENT_ID} ---")
    comment_update_url = f"/api/comments/{TEST_COMMENT_ID}"
    update_payload = {"body": "수정된 멋진 댓글 내용입니다."}
    call_api('PUT', comment_update_url, token=auth_token, json_data=update_payload)
    
    # 5. 댓글 삭제 테스트 (DELETE)
    print(f"\n--- 5. 댓글 삭제 테스트 (DELETE) - ID: {TEST_COMMENT_ID} ---")
    call_api('DELETE', comment_update_url, token=auth_token)

    # 6. 삭제 후 목록 재조회
    print("\n--- 6. 삭제 후 목록 재조회 (확인) ---")
    call_api('GET', comment_create_url)