# server_comment.py
# 댓글 데이터베이스 CRUD 로직을 담당하는 모듈

import mysql.connector
from db_utils import get_connection, close_connection
from datetime import datetime

# -------------------------- 1. 댓글 생성 (Create) --------------------------
def create_comment(post_id, user_id, comment_body):
    conn = get_connection()
    if not conn:
        return {"status": "FAILURE", "message": "DB 연결 실패"}

    try:
        cursor = conn.cursor()
        
        # a. 댓글 삽입
        insert_query = """
        INSERT INTO comments (post_id, user_id, comment_body, created_at, updated_at) 
        VALUES (%s, %s, %s, %s, %s)
        """
        now = datetime.now()
        cursor.execute(insert_query, (post_id, user_id, comment_body, now, now))
        
        # b. posts 테이블의 comment_count 증가
        update_count_query = "UPDATE posts SET comment_count = comment_count + 1 WHERE post_id = %s"
        cursor.execute(update_count_query, (post_id,))
        
        conn.commit()
        return {"status": "SUCCESS", "message": "댓글이 성공적으로 작성되었습니다."}

    except mysql.connector.Error as e:
        conn.rollback() 
        return {"status": "FAILURE", "message": f"DB 처리 중 오류 발생: {e}"}

    finally:
        close_connection(conn)

# -------------------------- 2. 댓글 조회 (Read) --------------------------
def get_comments_by_post(post_id):
    conn = get_connection()
    if not conn:
        return {"status": "FAILURE", "message": "DB 연결 실패"}

    try:
        cursor = conn.cursor(dictionary=True) # 딕셔너리 형태로 결과 받기
        
        # users 테이블과 조인하여 작성자의 이름(profiles.name)을 함께 조회하는 것이 일반적
        # 현재 profiles 테이블에 'name'을 닉네임으로 가정하고 조회
        select_query = """
        SELECT c.comment_id, c.comment_body, c.created_at, u.id AS user_id, p.name AS nickname
        FROM comments c
        JOIN users u ON c.user_id = u.id
        LEFT JOIN profiles p ON u.id = p.user_id
        WHERE c.post_id = %s
        ORDER BY c.created_at ASC
        """
        cursor.execute(select_query, (post_id,))
        comments = cursor.fetchall()
        
        # 댓글이 없어도 SUCCESS로 반환 (빈 배열)
        if not comments:
            return {"status": "SUCCESS", "comments": []}

        # 날짜/시간 포맷팅
        for comment in comments:
            comment['created_at'] = comment['created_at'].strftime("%Y-%m-%d %H:%M:%S")

        return {"status": "SUCCESS", "comments": comments}

    except mysql.connector.Error as e:
        return {"status": "FAILURE", "message": f"DB 처리 중 오류 발생: {e}"}

    finally:
        close_connection(conn)

# -------------------------- 3. 댓글 수정 (Update) --------------------------
def update_comment(comment_id, user_id, new_body):
    conn = get_connection()
    if not conn:
        return {"status": "FAILURE", "message": "DB 연결 실패"}

    try:
        cursor = conn.cursor()
        
        # a. 권한 확인: 해당 댓글의 user_id가 요청한 user_id와 일치하는지 확인
        check_owner_query = "SELECT user_id FROM comments WHERE comment_id = %s"
        cursor.execute(check_owner_query, (comment_id,))
        result = cursor.fetchone()

        if not result:
            return {"status": "FAILURE", "message": "댓글을 찾을 수 없습니다."}
        
        if result[0] != user_id:
            return {"status": "FAILURE", "message": "권한 없음"} # 403 Forbidden

        # b. 댓글 수정
        update_query = """
        UPDATE comments SET comment_body = %s, updated_at = %s 
        WHERE comment_id = %s
        """
        now = datetime.now()
        cursor.execute(update_query, (new_body, now, comment_id))
        
        conn.commit()
        return {"status": "SUCCESS", "message": "댓글이 성공적으로 수정되었습니다."}

    except mysql.connector.Error as e:
        conn.rollback() 
        return {"status": "FAILURE", "message": f"DB 처리 중 오류 발생: {e}"}

    finally:
        close_connection(conn)

# -------------------------- 4. 댓글 삭제 (Delete) --------------------------
def delete_comment(comment_id, user_id):
    conn = get_connection()
    if not conn:
        return {"status": "FAILURE", "message": "DB 연결 실패"}

    try:
        cursor = conn.cursor()
        
        # a. 권한 확인 (수정과 동일) 및 post_id 확인 (comment_count 감소용)
        check_query = "SELECT user_id, post_id FROM comments WHERE comment_id = %s"
        cursor.execute(check_query, (comment_id,))
        result = cursor.fetchone()

        if not result:
            return {"status": "FAILURE", "message": "댓글을 찾을 수 없습니다."}
        
        comment_owner_id, post_id = result
        
        if comment_owner_id != user_id:
            return {"status": "FAILURE", "message": "권한 없음"} # 403 Forbidden

        # b. 댓글 삭제
        delete_query = "DELETE FROM comments WHERE comment_id = %s"
        cursor.execute(delete_query, (comment_id,))
        
        # c. posts 테이블의 comment_count 감소
        update_count_query = "UPDATE posts SET comment_count = comment_count - 1 WHERE post_id = %s"
        cursor.execute(update_count_query, (post_id,))
        
        conn.commit()
        return {"status": "SUCCESS", "message": "댓글이 성공적으로 삭제되었습니다."}

    except mysql.connector.Error as e:
        conn.rollback() 
        return {"status": "FAILURE", "message": f"DB 처리 중 오류 발생: {e}"}

    finally:
        close_connection(conn)