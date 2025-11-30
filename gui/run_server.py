# run_server.py
# 웹 서버를 실행하고 DB 연결 상태를 확인하는 스크립트

import sys
from db_utils import get_connection

def check_db_connection():
    """DB 연결 상태를 확인합니다."""
    print("=" * 50)
    print("데이터베이스 연결 확인")
    print("=" * 50)
    
    conn = get_connection()
    if conn:
        print("✅ DB 연결 성공!")
        conn.close()
        return True
    else:
        print("❌ DB 연결 실패")
        print("\n해결 방법:")
        print("1. MySQL 서버가 실행 중인지 확인")
        print("2. db_config.py의 비밀번호가 올바른지 확인")
        print("3. MySQL Workbench에서 연결 테스트")
        return False

def check_database_exists():
    """ai_community 데이터베이스가 존재하는지 확인합니다."""
    try:
        from db_config import DB_CONFIG
        config_without_db = DB_CONFIG.copy()
        config_without_db.pop('database', None)
        
        import mysql.connector
        conn = mysql.connector.connect(**config_without_db)
        cursor = conn.cursor()
        
        cursor.execute("SHOW DATABASES LIKE 'ai_community'")
        result = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if result:
            print("✅ ai_community 데이터베이스 존재 확인")
            return True
        else:
            print("❌ ai_community 데이터베이스가 없습니다")
            print("\n해결 방법:")
            print("1. python setup_database.py 실행")
            print("2. 또는 MySQL Workbench에서 SQL 실행")
            return False
    except Exception as e:
        print(f"❌ 데이터베이스 확인 중 오류: {e}")
        return False

if __name__ == '__main__':
    print("\n웹 서버 실행 전 체크리스트\n")
    
    # 1. DB 연결 확인
    db_ok = check_db_connection()
    print()
    
    # 2. 데이터베이스 존재 확인
    db_exists = check_database_exists()
    print()
    
    if db_ok and db_exists:
        print("=" * 50)
        print("✅ 모든 준비 완료! 웹 서버를 실행합니다...")
        print("=" * 50)
        print("\n브라우저에서 http://127.0.0.1:5000 접속하세요")
        print("서버를 중지하려면 Ctrl+C를 누르세요\n")
        
        # 웹 서버 실행
        from server_main import community_API
        community_API.run(debug=True, host='127.0.0.1', port=5000)
    else:
        print("=" * 50)
        print("❌ 준비가 완료되지 않았습니다")
        print("=" * 50)
        print("\n위의 해결 방법을 따라주세요.")
        sys.exit(1)





