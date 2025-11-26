# test_CS_login_register.py
# 메인 클라이언트 모듈

from client_register import register_client
from client_login import login_client
import time

if __name__ == '__main__':
    
    TEST_EMAIL = "test_client123@test.com"
    TEST_PASSWORD = "testpass222@"
    
    print("클라이언트 테스트 프로그램 시작")
    # 1. 회원가입 테스트 (DB에 없을 경우 201 Created)
    register_client(TEST_EMAIL, TEST_PASSWORD)
    
    time.sleep(1) # 잠시 대기

    # 2. 로그인 테스트 (성공 시 200)
    login_client(TEST_EMAIL, TEST_PASSWORD)

    time.sleep(1)

    # 3. 실패하는 로그인 테스트 (비밀번호 오류, 401)
    login_client(TEST_EMAIL, "wrong_password")