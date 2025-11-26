# db_utils.py
# DB 연결 및 종료를 위한 유틸리티 함수들

import mysql.connector
from db_config import DB_CONFIG # DB 접속 정보 불러오기

def get_connection():
    #DB 연결 객체를 반환
    try:
        # DB_CONFIG 정보를 풀어 연결 함수에 전달
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as e:
        print(f"DB 연결 오류: {e}")
        # 연결에 실패하면 None 반환
        return None

def close_connection(conn):
    #DB 연결을 안전하게 종료
    if conn and conn.is_connected():
        conn.close()