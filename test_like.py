# test_like.py
# 좋아요(Like) 기능의 클라이언트-서버-DB 연동을 테스트하는 통합 테스트 코드

# 필요한 클라이언트 모듈들을 import
from client_register import register_client
from client_login import login_client
from client_like import toggle_post_like_client
import time

# -------------------------- 테스트 환경 설정 --------------------------

# 테스트 사용자 정보
TEST_USER_EMAIL = f"test@test.com"
TEST_PASSWORD = "abc123@"

# 테스트할 게시글 ID (실제 DB에 존재하는 ID를 가정하고 진행)
# 이 ID는 서버의 DB에 'posts' 테이블에 존재해야만 테스트가 성공함.
# 테스트를 위해 post_id 1번을 가정
TARGET_POST_ID = 1 

# -------------------------- 테스트 실행 함수 --------------------------

def run_like_test():
    print("=" * 60)
    print("        게시글 좋아요 기능 통합 테스트 시작")
    print("=" * 60)

    # 1. 회원가입
    print("\n--- 1. 사용자 회원가입 시도 ---")
    register_result = register_client(TEST_USER_EMAIL, TEST_PASSWORD)
    
    # 회원가입 성공/실패 여부 체크 (중복이 이미 있다면 무시)
    if register_result is not None and register_result.get("status") == "SUCCESS":
        print("[CHECK] 회원가입 성공.")
    elif register_result is None or register_result.get("message") == "이미 존재하는 이메일입니다.":
        print("[CHECK] 이미 등록된 사용자이거나 연결 오류. 다음 단계로 진행.")
    else:
        print("[FAIL] 회원가입 실패. 테스트 중단.")
        return

    # 2. 로그인 및 JWT 토큰 획득
    print("\n--- 2. 사용자 로그인 및 토큰 획득 시도 ---")
    login_result = login_client(TEST_USER_EMAIL, TEST_PASSWORD)
    
    if login_result and login_result.get("status") == "SUCCESS":
        access_token = login_result.get("access_token")
        user_id = login_result.get("user_id")
        print(f"[CHECK] 로그인 성공. User ID: {user_id}, 토큰 획득 완료.")
    else:
        print("[FAIL] 로그인 실패. 테스트 중단.")
        return

    # 3. 좋아요 토글 (LIKE)
    print(f"\n--- 3. 게시글 ID {TARGET_POST_ID}에 좋아요 추가 (LIKE) 시도 ---")
    like_result_1 = toggle_post_like_client(TARGET_POST_ID, access_token)
    
    if like_result_1 and like_result_1.get("status") == "SUCCESS" and like_result_1.get("action") == "LIKE":
        print("[SUCCESS] 좋아요 추가 성공. 서버의 post_likes 테이블과 posts.like_count 확인 필요.")
    else:
        print(f"[FAIL] 좋아요 추가 실패. 응답: {like_result_1.get('message', 'None')}")
        # 테스트는 계속 진행하여 취소 로직을 확인
        pass 

   # 4. 좋아요 토글 (UNLIKE) - 취소
    print(f"\n--- 4. 게시글 ID {TARGET_POST_ID}에 좋아요 취소 (UNLIKE) 시도 ---")
    # 잠시 딜레이를 주어 API 호출 시점을 분리 (선택 사항)
    time.sleep(1) 
    unlike_result = toggle_post_like_client(TARGET_POST_ID, access_token)
    
    if unlike_result and unlike_result.get("status") == "SUCCESS" and unlike_result.get("action") == "UNLIKE":
        print("[SUCCESS] 좋아요 취소 성공. 서버의 post_likes 레코드 제거와 posts.like_count 감소 확인 필요.")
    else:
        print(f"[FAIL] 좋아요 취소 실패. 응답: {unlike_result.get('message', 'None')}")
        pass

# 파일이 직접 실행될 때 테스트 함수 호출
if __name__ == '__main__':
    run_like_test()
