# server_like.py
# 게시글 좋아요(Like) 및 좋아요 취소(Unlike) 로직을 담당하는 모듈

import mysql.connector
from db_utils import get_connection, close_connection

# -------------------------- 좋아요 토글 로직 (Like/Unlike Toggle) --------------------------
def toggle_post_like(post_id, user_id):
    # param post_id: 좋아요/취소할 게시글의 ID
    # param user_id: 요청을 보낸 사용자의 ID (인증 필수)
    # return: 딕셔너리 형태의 결과 (SUCCESS/FAILURE, 메시지)

    conn = get_connection()
    if not conn:
        # DB 연결 실패 시
        return {"status": "FAILURE", "message": "DB 연결 실패"}

    try:
        cursor = conn.cursor()

        # 1. post_likes 테이블에서 사용자가 이미 '좋아요'를 눌렀는지 확인
        check_query = """
        SELECT COUNT(*) 
        FROM post_likes 
        WHERE user_id = %s AND post_id = %s
        """
        cursor.execute(check_query, (user_id, post_id))
        is_liked = cursor.fetchone()[0] > 0 # 좋아요를 이미 눌렀으면 True

        if is_liked:
            # 2. 이미 좋아요를 눌렀다면 -> 좋아요 취소 (Unlike)
            
            # a. post_likes 테이블에서 레코드 삭제
            delete_query = "DELETE FROM post_likes WHERE user_id = %s AND post_id = %s"
            cursor.execute(delete_query, (user_id, post_id))
            
            # b. posts 테이블의 like_count 1 감소
            update_count_query = "UPDATE posts SET like_count = like_count - 1 WHERE post_id = %s"
            cursor.execute(update_count_query, (post_id,))
            
            action = "UNLIKE"
            message = "좋아요가 취소되었습니다."
        
        else:
            # 3. 좋아요를 누르지 않았다면 -> 좋아요 추가 (Like)
            
            # a. post_likes 테이블에 레코드 삽입
            insert_query = """
            INSERT INTO post_likes (user_id, post_id) 
            VALUES (%s, %s)
            """
            cursor.execute(insert_query, (user_id, post_id))
            
            # b. posts 테이블의 like_count 1 증가
            update_count_query = "UPDATE posts SET like_count = like_count + 1 WHERE post_id = %s"
            cursor.execute(update_count_query, (post_id,))
            
            action = "LIKE"
            message = "좋아요가 성공적으로 반영되었습니다."
            
        # 4. 모든 DB 작업(삽입/삭제 및 카운트 업데이트)을 확정 (트랜잭션)
        conn.commit()
        return {"status": "SUCCESS", "action": action, "message": message}

    except mysql.connector.Error as e:
        # DB 작업 중 오류 발생 시
        conn.rollback() # 오류 발생 시 이전에 수행된 모든 작업 취소 (트랜잭션 롤백)
        return {"status": "FAILURE", "message": f"DB 처리 중 오류 발생: {e}"}
        
    finally:
        # DB 연결을 안전하게 종료
        close_connection(conn)