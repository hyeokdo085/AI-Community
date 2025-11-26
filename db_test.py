# db_test.py
# 이 파일은 데이터베이스와 연결되는지 테스트하는 용도임

import mysql.connector
from db_config import DB_CONFIG # 1. db_config.py에서 설정 정보 가져오기.

def test_db_connection():
    conn = None # 연결 객체 변수
    try:
        # 2. DB_CONFIG 정보 사용, MySQL에 연결 시도
        conn = mysql.connector.connect(**DB_CONFIG)
        
        # 3. 연결에 성공했는지 확인
        if conn.is_connected():
            print("DB 연결 성공")
            
            # 4. 간단한 SQL 쿼리 실행 테스트
            cursor = conn.cursor()
            cursor.execute("SELECT DATABASE()") # 현재 접속된 DB 이름을 가져오는 SQL
            db_name = cursor.fetchone()[0]
            print(f"현재 접속된 데이터베이스 이름: {db_name}")
            cursor.close()

    except mysql.connector.Error as e:
        # 5. 연결 실패 시 오류 메시지 출력
        print(f"DB 연결 실패 : {e}")

    finally:
        # 6. 연결 후 연결을 닫아 자원 해제
        if conn and conn.is_connected():
            conn.close()
            print("DB 연결이 종료되었습니다.")

# 이 파일이 직접 실행될 때 test_db_connection 함수 호출
if __name__ == '__main__':
    test_db_connection()