# db_config.py

# DB 연결에 필요한 기본 정보들을 정의.
DB_CONFIG = {
    # 1. Host: MySQL이 설치된 컴퓨터 주소 (내 컴퓨터: 127.0.0.1 또는 localhost)
    'host': '127.0.0.1',      
    
    # 2. User: MySQL에서 사용자 이름
    'user': 'root',      
    
    # 3. Password: MySQL Workbench 비밀번호
    'password': 'root',  
    
    # 4. Database: MySQL Workbench에서 만든 DB 이름
    'database': 'ai_community', 
    
    # 5. Port: MySQL의 기본 포트 번호
    'port': 3306              
}

# 이 파일은 절대로 외부에 노출 금지!!!!!!!!!!!!