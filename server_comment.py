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
        INSERT INTO comments (post_id, user_id, comment_body) 
        VALUES (%s, %s, %s)
        """
        cursor.execute(insert_query, (post_id, user_id, comment_body))
        
        # [안정성 유지] 삽입된 ID를 SELECT LAST_INSERT_ID()를 사용하여 명확하게 가져옴
        cursor.execute("SELECT LAST_INSERT_ID()")
        new_comment_id = cursor.fetchone()[0]
        
        # b. posts 테이블의 comment_count 증가
        update_count_query = "UPDATE posts SET comment_count = comment_count + 1 WHERE post_id = %s"
        cursor.execute(update_count_query, (post_id,))
        
        conn.commit()
        # 삽입된 댓글 ID를 반환하여 클라이언트에서 활용할 수 있게 함
        return {"status": "SUCCESS", "message": "댓글이 성공적으로 작성되었습니다.", "comment_id": new_comment_id}

    except mysql.connector.Error as e:
        conn.rollback() 
        return {"status": "FAILURE", "message": f"DB 처리 중 오류 발생: {e}"}

    finally:
        close_connection(conn)

# -------------------------- 2. 댓글 목록 조회 (Read) --------------------------
def get_comments_by_post(post_id):
    conn = get_connection()
    if not conn:
        return {"status": "FAILURE", "message": "DB 연결 실패"}

    try:
        cursor = conn.cursor()
        
        # 댓글과 작성자 정보를 함께 조회: profiles 테이블의 name을 가져옴
        # LEFT JOIN profiles를 사용하여 profiles 테이블에 항목이 없더라도 조회 가능하게 함
        # COALESCE를 사용하여 name이 NULL일 경우 '익명'으로 표시
        select_query = """
        SELECT c.comment_id, c.comment_body, c.created_at, COALESCE(p.name, '익명') AS user_name
        FROM comments c
        LEFT JOIN profiles p ON c.user_id = p.user_id
        WHERE c.post_id = %s
        ORDER BY c.created_at ASC
        """
        cursor.execute(select_query, (post_id,))
        rows = cursor.fetchall()
        
        comments_list = []
        for row in rows:
            comment = {
                "comment_id": row[0],
                "body": row[1],
                "created_at": row[2].strftime("%Y-%m-%d %H:%M:%S") if isinstance(row[2], datetime) else str(row[2]),
                "user_name": row[3] 
            }
            comments_list.append(comment)
            
        if not comments_list:
            return {"status": "FAILURE", "message": "해당 게시글에 댓글이 없습니다."}
            
        return {"status": "SUCCESS", "comments": comments_list, "total_comments": len(comments_list)}

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
        
        # a. 권한 확인: 댓글 작성자 ID와 수정 요청자 ID가 일치하는지 확인
        check_query = "SELECT user_id FROM comments WHERE comment_id = %s"
        cursor.execute(check_query, (comment_id,))
        result = cursor.fetchone()

        if not result:
            return {"status": "FAILURE", "message": "댓글을 찾을 수 없습니다."}
        
        comment_owner_id = result[0]
        
        if comment_owner_id != user_id:
            return {"status": "FAILURE", "message": "권한 없음"} # 403 Forbidden
            
        # b. 댓글 수정
        update_query = "UPDATE comments SET comment_body = %s WHERE comment_id = %s"
        cursor.execute(update_query, (new_body, comment_id))
        
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