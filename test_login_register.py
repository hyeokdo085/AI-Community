# test_login_register.py
# 회원가입 및 로그인 기능을 테스트

from server_login_register import register_user, login_user

# 테스트에 사용할 정보
TEST_EMAIL = "test@test.com"
TEST_PASSWORD = "abc123@"

print("--- 1. 회원가입 테스트 ---")
result_reg = register_user(TEST_EMAIL, TEST_PASSWORD)
print(f"회원가입 결과: {result_reg}")

print("\n--- 2. 중복 회원가입 테스트 ---")
result_reg_dup = register_user(TEST_EMAIL, TEST_PASSWORD)
print(f"중복 회원가입 결과: {result_reg_dup}")

print("\n--- 3. 로그인 성공 테스트 ---")
result_login_success = login_user(TEST_EMAIL, TEST_PASSWORD)
print(f"로그인 성공 결과: {result_login_success}")

print("\n--- 4. 로그인 실패 테스트 (비밀번호 오류) ---")
result_login_fail = login_user(TEST_EMAIL, "wrongpassword")
print(f"로그인 실패 결과: {result_login_fail}")