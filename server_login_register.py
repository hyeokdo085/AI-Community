# server_login_register.py
# 회원가입 및 로그인 기능을 담당하는 모듈

import mysql.connector
from flask_bcrypt import Bcrypt
from db_utils import get_connection, close_connection

# 1. Bcrypt 객체 생성 (비밀번호 암호화를 위한 도구)
bcrypt = Bcrypt()

# A. 회원가입 로직
def register_user(email, password):
    # 새 사용자를 등록, DB에 저장
    conn = get_connection()
    if not conn: # DB 연결 실패 시
        return {"status": "FAILURE", "message": "DB 연결 실패"}

    try:
        cursor = conn.cursor()
        
        # 1. 이메일 중복 확인
        check_query = "SELECT id FROM users WHERE email = %s"
        cursor.execute(check_query, (email,))
        if cursor.fetchone():
            return {"status": "FAILURE", "message": "이미 존재하는 이메일입니다."}
            
        # 2. 비밀번호 해싱 
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        
        # 3. DB에 사용자 정보 삽입
        insert_user_query = "INSERT INTO users (email, password) VALUES (%s, %s)"
        cursor.execute(insert_user_query, (email, hashed_password))
        
        # 4. DB에 실제로 저장되도록 확정
        conn.commit()

        return {"status": "SUCCESS", "message": "회원가입이 완료되었습니다."}

    except mysql.connector.Error as e:
        # 오류 발생 시 저장된 내용 취소
        conn.rollback() 
        return {"status": "FAILURE", "message": f"DB 처리 중 오류 발생: {e}"}

    finally:
        close_connection(conn)

# B. 로그인 로직 (Login)
def login_user(email, password):
    # 이메일과 비밀번호를 검증, 성공 시 사용자 ID를 반환.
    conn = get_connection()
    if not conn: # DB 연결 실패 시
        return {"status": "FAILURE", "message": "DB 연결 실패"}
        
    try:
        cursor = conn.cursor()
        
        # 1. 이메일로 사용자 정보 조회
        select_query = "SELECT id, password FROM users WHERE email = %s"
        cursor.execute(select_query, (email,))
        result = cursor.fetchone()
        
        if not result:
            # 해당 이메일을 가진 사용자가 없으면
            return {"status": "FAILURE", "message": "사용자 이름 또는 비밀번호가 잘못되었습니다."}
        
        user_id, hashed_password_from_db = result
        
        # 2. 비밀번호 일치 확인 (암호화된 비밀번호와 비교)
        # 입력된 비밀번호를 암호화하여 DB의 해시 값과 비교
        if bcrypt.check_password_hash(hashed_password_from_db, password):
            # 비밀번호 일치
            
            # TODO: ID를 생성하고 반환하는 로직이 추가
            return {"status": "SUCCESS", "user_id": user_id, "message": "로그인 성공"}
        else:
            # 비밀번호 불일치
            return {"status": "FAILURE", "message": "사용자 이름 또는 비밀번호가 잘못되었습니다."}

    except mysql.connector.Error as e:
        return {"status": "FAILURE", "message": f"DB 처리 중 오류 발생: {e}"}
        
    finally:
        close_connection(conn)