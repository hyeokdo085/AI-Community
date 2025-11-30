# setup_database.py
# DB 스키마를 생성하는 스크립트

import mysql.connector
from db_config import DB_CONFIG

def create_database():
    """DB 스키마와 테이블을 생성합니다."""
    # 먼저 DB 없이 연결 (스키마 생성용)
    config_without_db = DB_CONFIG.copy()
    config_without_db.pop('database', None)
    
    conn = None
    try:
        # DB 연결 (스키마 없이)
        conn = mysql.connector.connect(**config_without_db)
        cursor = conn.cursor()
        
        print("MySQL 서버 연결 성공!")
        
        # 스키마 생성
        print("\n1. 스키마 생성 중...")
        cursor.execute("""
            CREATE SCHEMA IF NOT EXISTS ai_community 
            DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
        """)
        print("   ✓ ai_community 스키마 생성 완료")
        
        # DB 선택
        cursor.execute("USE ai_community")
        
        # 테이블 생성
        print("\n2. 테이블 생성 중...")
        
        # users 테이블
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT PRIMARY KEY AUTO_INCREMENT,
                password VARCHAR(255) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                role ENUM('user', 'admin') DEFAULT 'user'
            )
        """)
        print("   ✓ users 테이블 생성 완료")
        
        # profiles 테이블
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS profiles (
                user_id INT PRIMARY KEY,
                name VARCHAR(30),
                bio VARCHAR(100),
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        print("   ✓ profiles 테이블 생성 완료")
        
        # posts 테이블
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS posts (
                post_id INT PRIMARY KEY AUTO_INCREMENT,
                user_id INT NOT NULL,
                title VARCHAR(100),
                body TEXT,
                pinned BOOLEAN DEFAULT FALSE,
                private BOOLEAN DEFAULT FALSE,
                view_count INT DEFAULT 0,
                comment_count INT DEFAULT 0,
                like_count INT DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        print("   ✓ posts 테이블 생성 완료")
        
        # comments 테이블
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS comments (
                comment_id INT PRIMARY KEY AUTO_INCREMENT,
                post_id INT NOT NULL,
                user_id INT NOT NULL,
                comment_body TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (post_id) REFERENCES posts(post_id),
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        print("   ✓ comments 테이블 생성 완료")
        
        # post_likes 테이블
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS post_likes (
                user_id INT NOT NULL,
                post_id INT NOT NULL,
                PRIMARY KEY (user_id, post_id),
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (post_id) REFERENCES posts(post_id)
            )
        """)
        print("   ✓ post_likes 테이블 생성 완료")
        
        conn.commit()
        print("\n✅ 모든 테이블 생성 완료!")
        
        # 테이블 목록 확인
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print(f"\n생성된 테이블 목록: {[table[0] for table in tables]}")
        
        cursor.close()
        
    except mysql.connector.Error as e:
        print(f"\n❌ 오류 발생: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn and conn.is_connected():
            conn.close()
            print("\nDB 연결 종료")

if __name__ == '__main__':
    print("=" * 50)
    print("AI Community 데이터베이스 설정")
    print("=" * 50)
    create_database()





