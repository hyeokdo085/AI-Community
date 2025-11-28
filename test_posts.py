# test_posts.py
# 게시글 클라이언트 기능 (client_posts.py) 테스트 코드

import sys
import json
# 로컬 모듈 import
from client_register import register_client
from client_login import login_client
from client_posts import (
    create_post_client,
    get_all_posts_client,
    get_post_detail_client,
    update_post_client,
    delete_post_client
)

# -------------------------- 테스트용 사용자 정보 --------------------------
USER_EMAIL_1 = "test_user_posts_5@example.com"
USER_PASS_1 = "postuser1234" # 게시글 작성자
USER_EMAIL_2 = "test_user_posts_6@example.com"
USER_PASS_2 = "postuser5678" # 타인 (권한 테스트용)

# -------------------------- 테스트용 게시글 정보 --------------------------
TEST_TITLE_PUBLIC = "일반 공개 게시글"
TEST_TITLE_PRIVATE = "비공개 테스트 게시글"
TEST_BODY = "테스트 본문"
UPDATED_TITLE = "[수정됨] 새 테스트 제목"
UPDATED_BODY = "[수정됨] 새 본문 내용입니다."

# -------------------------- 테스트 유틸리티 --------------------------

def print_test_status(test_name, success, message=""):
    """테스트 결과 출력 포맷팅 함수"""
    status = "✅ 성공" if success else "❌ 실패"
    print(f"\n[{status}] {test_name}: {message}")
    if not success:
        print("-------------------- 테스트 중단 --------------------")
        sys.exit(1) # 실패 시 테스트 중단

def setup_users():
    """테스트에 필요한 사용자 등록 및 로그인/토큰 확보"""
    print("================== 사용자 설정 시작 ==================")

    # 1. 사용자 1 등록 및 로그인
    register_client(USER_EMAIL_1, USER_PASS_1)
    login_result_1 = login_client(USER_EMAIL_1, USER_PASS_1)
    if login_result_1 and login_result_1.get('status') == 'SUCCESS':
        access_token_1 = login_result_1.get('access_token')
        print(f"사용자 1 토큰 확보: {access_token_1[:10]}...")
    else:
        print_test_status("사용자 1 로그인", False, "사용자 1 로그인 실패")
        return None, None
    
    # 2. 사용자 2 등록 및 로그인 (권한 테스트용)
    register_client(USER_EMAIL_2, USER_PASS_2)
    login_result_2 = login_client(USER_EMAIL_2, USER_PASS_2)
    if login_result_2 and login_result_2.get('status') == 'SUCCESS':
        access_token_2 = login_result_2.get('access_token')
        print(f"사용자 2 토큰 확보: {access_token_2[:10]}...")
    else:
        print_test_status("사용자 2 로그인", False, "사용자 2 로그인 실패")
        return access_token_1, None
        
    print("================== 사용자 설정 완료 ==================\n")
    return access_token_1, access_token_2


# -------------------------- 메인 테스트 로직 --------------------------
def main_test():
    # 1. 사용자 설정 및 토큰 확보 (setup_users 함수는 이전과 동일하다고 가정)
    access_token_1, access_token_2 = setup_users()
    if not access_token_1 or not access_token_2:
        return

    public_post_id = None
    private_post_id = None
    
    # ========================== [Test 1] 일반 공개 게시글 생성 ==========================
    print("\n--- [Test 1] 일반 공개 게시글 생성 ---")
    create_res_public = create_post_client(access_token_1, TEST_TITLE_PUBLIC, TEST_BODY, pinned=False, private=False)
    
    if create_res_public and create_res_public.get('status') == 'SUCCESS' and 'post_id' in create_res_public:
        public_post_id = create_res_public.get('post_id')
        print_test_status("공개 게시글 생성", True, f"ID: {public_post_id}")
    else:
        print_test_status("공개 게시글 생성", False, f"응답: {create_res_public}"); return

    # ========================== [Test 2] 비공개 게시글 생성 (Private) ==========================
    print("\n--- [Test 2] 비공개 게시글 생성 ---")
    create_res_private = create_post_client(access_token_1, TEST_TITLE_PRIVATE, TEST_BODY, pinned=False, private=True)
    
    if create_res_private and create_res_private.get('status') == 'SUCCESS' and 'post_id' in create_res_private:
        private_post_id = create_res_private.get('post_id')
        print_test_status("비공개 게시글 생성", True, f"ID: {private_post_id}")
    else:
        print_test_status("비공개 게시글 생성", False, f"응답: {create_res_private}"); return

    # ========================== [Test 3] 게시글 목록 조회 (Private 필터링 확인) ==========================
    print("\n--- [Test 3] 게시글 목록 조회 (Private 필터링 확인) ---")
    list_res = get_all_posts_client()
    
    found_public = False
    found_private = False
    if list_res and list_res.get('status') == 'SUCCESS' and list_res.get('posts'):
        for post in list_res['posts']:
            if post.get('post_id') == public_post_id:
                found_public = True
            if post.get('post_id') == private_post_id:
                found_private = True
                
        is_correct = found_public and not found_private
        print_test_status("목록 조회", is_correct, f"공개 ({found_public}), 비공개 ({found_private}) - 비공개 게시글 제외 확인")
    else:
        print_test_status("목록 조회", False, f"응답: {list_res}")

    # ========================== [Test 4] 게시글 상세 조회 및 View Count 증가 확인 ==========================
    print("\n--- [Test 4] 상세 조회 (View Count) ---")
    detail_res_1 = get_post_detail_client(public_post_id)
    detail_res_2 = get_post_detail_client(public_post_id)
    
    view_count_1 = detail_res_1.get('post', {}).get('view_count', 0)
    view_count_2 = detail_res_2.get('post', {}).get('view_count', 0)
    
    is_vc_incremented = (view_count_2 == view_count_1 + 1)
    print_test_status("조회수 증가", is_vc_incremented, f"View Count: 1차 {view_count_1}, 2차 {view_count_2} -> 증가 확인")

    # ========================== [Test 5] Private 게시글 접근 권한 테스트 (타인 접근) ==========================
    print("\n--- [Test 5] Private 게시글 타인 접근 시도 ---")
    # 타인은 access_token을 넘기지 않으므로, 요청자 user_id가 None인 상황을 가정 (API 로직으로 해결 필요)
    # 현재 API 로직에서는 토큰 없이 호출하면 무조건 None으로 처리됩니다.
    unauth_detail_res = get_post_detail_client(private_post_id) 
    
    is_unauth_fail = (
        unauth_detail_res and unauth_detail_res.get('status') == 'FAILURE' and 
        unauth_detail_res.get('message') == '비공개 게시글이거나, 접근 권한이 없습니다.'
    )
    print_test_status("Private 게시글 타인 접근", is_unauth_fail, "403 접근 권한 없음 응답 확인")
    
    # ========================== [Test 6] 게시글 수정 (Update - pinned/private) ==========================
    print("\n--- [Test 6] 게시글 수정 (Pinned 및 Private 변경) ---")
    update_res = update_post_client(
        public_post_id, access_token_1, UPDATED_TITLE, UPDATED_BODY, new_pinned=True, new_private=True
    )
    is_update_success = update_res and update_res.get('status') == 'SUCCESS'
    print_test_status("게시글 수정", is_update_success, "수정 성공 메시지 확인")
    
    # 수정된 게시글이 private이 되었으므로, 목록에서 사라졌는지 확인 (선택 사항)
    
    # ========================== [Test 7] 게시글 삭제 (Delete - private 게시글) ==========================
    print("\n--- [Test 7] 게시글 삭제 테스트 (Private 게시글) ---")
    delete_res = delete_post_client(private_post_id, access_token_1)
    
    is_delete_success = delete_res and delete_res.get('status') == 'SUCCESS'
    print_test_status("게시글 삭제 (Private)", is_delete_success, "삭제 성공 메시지 확인")

    print("\n\n================== 모든 테스트 완료 ==================")

if __name__ == '__main__':
    main_test()