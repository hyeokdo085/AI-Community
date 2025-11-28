# test_comment_client.py
# 댓글 기능의 클라이언트-서버-DB 연동을 테스트하는 통합 테스트 코드

from client_register import register_client
from client_login import login_client
from client_comment import create_comment_client, get_comments_client, update_comment_client, delete_comment_client
import time

# -------------------------- 테스트 환경 설정 --------------------------

# 테스트 사용자 정보
TEST_USER_EMAIL = f"comment_user_{int(time.time())}@test.com"
TEST_PASSWORD = "testpassword123!"

# 다른 사용자 정보 (권한 테스트용)
OTHER_USER_EMAIL = f"other_user_{int(time.time())}@test.com"

# 테스트할 게시글 ID (DB에 존재하는 ID를 가정)
TARGET_POST_ID = 1 

# -------------------------- 테스트 실행 함수 --------------------------

def run_comment_test():
    print("=" * 60)
    print("        댓글 기능 통합 테스트 시작 (작성자 이메일 확인)")
    print("=" * 60)

    # 1. 사용자 회원가입 및 로그인
    print("\n--- 1. 사용자 1 (작성자) 회원가입 및 로그인 ---")
    register_client(TEST_USER_EMAIL, TEST_PASSWORD)
    login_result = login_client(TEST_USER_EMAIL, TEST_PASSWORD)
    
    if login_result and login_result.get("status") == "SUCCESS":
        main_token = login_result.get("access_token")
        print(f"[CHECK] 로그인 성공. 사용자 이메일: {TEST_USER_EMAIL}")
    else:
        print("[FAIL] 로그인 실패. 테스트 중단.")
        return

    # 2. 다른 사용자 로그인 (권한 테스트용)
    print("\n--- 2. 사용자 2 (타인) 회원가입 및 로그인 ---")
    register_client(OTHER_USER_EMAIL, TEST_PASSWORD)
    other_login_result = login_client(OTHER_USER_EMAIL, TEST_PASSWORD)
    other_token = other_login_result.get("access_token") if other_login_result and other_login_result.get("status") == "SUCCESS" else None

    # 3. 댓글 생성 (사용자 1)
    print(f"\n--- 3. 게시글 ID {TARGET_POST_ID}에 댓글 생성 시도 (작성자: {TEST_USER_EMAIL}) ---")
    initial_comment = "첫 번째 댓글입니다. (생성 테스트)"
    create_result = create_comment_client(TARGET_POST_ID, main_token, initial_comment)
    
    if create_result and create_result.get("status") == "SUCCESS":
        created_comment_id = create_result.get("comment_id")
        print(f"[SUCCESS] 댓글 생성 성공. ID: {created_comment_id}")
    else:
        print(f"[FAIL] 댓글 생성 실패. 응답: {create_result}")
        return

    # 4. 댓글 목록 조회 및 이메일 확인 (Read)
    print(f"\n--- 4. 댓글 목록 조회 및 작성자 이메일 확인 ---")
    comments_list_result = get_comments_client(TARGET_POST_ID)
    
    if comments_list_result and comments_list_result.get("status") == "SUCCESS":
        print(f"[SUCCESS] 댓글 총 {comments_list_result.get('total_comments')}개 조회 성공.")
        
        # 목록에서 첫 번째 댓글의 user_email 확인
        first_comment = comments_list_result["comments"][0]
        
        # user_email 필드가 있는지, 그리고 그 값이 맞는지 확인
        if "user_email" in first_comment and first_comment["user_email"] == TEST_USER_EMAIL:
            print(f"[CHECK] 작성자 이메일 필드 확인 완료: {first_comment['user_email']}")
            print(f"[CHECK] 댓글 내용: {first_comment['body']}")
        else:
            print(f"[FAIL] 댓글 작성자 이메일 필드 오류. 서버 응답 확인 필요.")
    else:
        print(f"[FAIL] 댓글 목록 조회 실패. 응답: {comments_list_result}")
        return


    # 5. 댓글 수정 시도 (Update) - 성공 (본인)
    print(f"\n--- 5. 댓글 수정 시도 (본인 권한) ---")
    updated_comment_body = "수정된 댓글 내용입니다."
    update_result_self = update_comment_client(created_comment_id, main_token, updated_comment_body)
    
    if update_result_self and update_result_self.get("status") == "SUCCESS":
        print("[SUCCESS] 댓글 수정 성공 (본인).")
    else:
        print(f"[FAIL] 댓글 수정 실패 (본인). 응답: {update_result_self}")


    # 6. 댓글 수정 시도 (Update) - 실패 (타인)
    print(f"\n--- 6. 댓글 수정 시도 (타인 권한) ---")
    update_result_other = update_comment_client(created_comment_id, other_token, "타인이 수정하려는 내용")
    
    if update_result_other and update_result_other.get("message") == "권한 없음":
        print("[SUCCESS] 댓글 수정 실패 (타인) - 권한 없음 응답 확인.")
    else:
        print(f"[FAIL] 댓글 수정 실패 (타인) - 예상치 못한 응답: {update_result_other}")


    # 7. 댓글 삭제 시도 (Delete) - 성공 (본인)
    print(f"\n--- 7. 댓글 삭제 시도 (본인 권한) ---")
    delete_result_self = delete_comment_client(created_comment_id, main_token)
    
    if delete_result_self and delete_result_self.get("status") == "SUCCESS":
        print("[SUCCESS] 댓글 삭제 성공 (본인).")
    else:
        print(f"[FAIL] 댓글 삭제 실패 (본인). 응답: {delete_result_self}")
        
    # 8. 삭제 후 댓글 목록 재조회 (비어 있어야 함)
    print(f"\n--- 8. 댓글 삭제 후 재조회 ---")
    final_check_result = get_comments_client(TARGET_POST_ID)
    
    if final_check_result and final_check_result.get("message") == "해당 게시글에 댓글이 없습니다.":
        print("[SUCCESS] 댓글 삭제 후 목록 비어있음 확인.")
    else:
        print(f"[FAIL] 댓글 삭제 후 재조회 오류. 응답: {final_check_result}")

    print("\n" + "=" * 60)
    print("        댓글 기능 통합 테스트 완료")
    print("=" * 60)

# 파일이 직접 실행될 때 테스트 함수 호출
if __name__ == '__main__':
    run_comment_test()