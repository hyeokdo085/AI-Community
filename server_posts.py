# server_posts.py
# 게시글 데이터베이스 CRUD 로직을 담당하는 모듈

import mysql.connector
from db_utils import get_connection, close_connection
from datetime import datetime



# -------------------------- 1. 게시글 생성 (Create) --------------------------
# user_id: 게시글을 작성하는 사용자의 ID
# title: 게시글 제목
# body: 게시글 내용
# pinned: 게시글 고정 여부 (기본값 False)
# private: 게시글 비공개 여부 (기본값 False)
def create_post(user_id, title, body, pinned=False, private=False):
    # DB 연결 객체 가져오기
    conn = get_connection()
    if not conn:
        # DB 연결 실패 시 에러 반환
        return {"status": "FAILURE", "message": "DB 연결 실패"}

    try:
        cursor = conn.cursor()
        
        # 게시글 삽입 쿼리 (pinned, private 필드 포함)
        insert_query = """
        INSERT INTO posts (user_id, title, body, pinned, private) 
        VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, (user_id, title, body, pinned, private))
        
        # 생성된 게시글의 ID 가져오기
        cursor.execute("SELECT LAST_INSERT_ID()")
        new_post_id = cursor.fetchone()[0]
        
        # 변경 사항 DB에 확정
        conn.commit()
        # 성공 메시지와 생성된 ID 반환
        return {"status": "SUCCESS", "message": "게시글이 성공적으로 작성되었습니다.", "post_id": new_post_id}

    except mysql.connector.Error as e:
        # DB 오류 발생 시 롤백
        conn.rollback() 
        return {"status": "FAILURE", "message": f"DB 처리 중 오류 발생: {e}"}

    finally:
        # DB 연결 종료
        close_connection(conn)



# -------------------------- 2. 게시글 전체 목록 조회 (Read - List) --------------------------
def get_all_posts():
    # DB 연결 객체 가져오기
    conn = get_connection()
    if not conn:
        return {"status": "FAILURE", "message": "DB 연결 실패"}

    try:
        cursor = conn.cursor()
        
        # 게시글 정보 조회 쿼리
        # private=FALSE인 게시글만 조회
        # pinned=TRUE인 게시글이 최상단에 오도록 정렬, 그 후 최신순(created_at DESC) 정렬
        select_query = """
        SELECT 
            p.post_id, p.title, p.body, p.created_at, p.like_count, p.comment_count, 
            p.view_count, p.pinned, p.private, COALESCE(pr.name, '익명') AS user_name, p.user_id
        FROM posts p
        LEFT JOIN profiles pr ON p.user_id = pr.user_id
        WHERE p.private = FALSE
        ORDER BY p.pinned DESC, p.created_at DESC
        """
        cursor.execute(select_query)
        rows = cursor.fetchall()
        
        posts_list = []
        # 조회된 결과를 JSON 형태로 변환
        for row in rows:
            post = {
                "post_id": row[0],
                "title": row[1],
                "body": row[2],
                # 날짜/시간 형식 변환
                "created_at": row[3].strftime("%Y-%m-%d %H:%M:%S") if isinstance(row[3], datetime) else str(row[3]),
                "like_count": row[4],
                "comment_count": row[5],
                "view_count": row[6],
                "pinned": bool(row[7]),
                "private": bool(row[8]),
                "user_name": row[9],
                "user_id": row[10]
            }
            posts_list.append(post)
            
        # 성공 메시지, 게시글 목록, 총 개수 반환
        return {"status": "SUCCESS", "posts": posts_list, "total_posts": len(posts_list)}

    except mysql.connector.Error as e:
        return {"status": "FAILURE", "message": f"DB 처리 중 오류 발생: {e}"}

    finally:
        # DB 연결 종료
        close_connection(conn)




# -------------------------- 3. 게시글 상세 조회 (Read - Detail) --------------------------
# post_id: 조회할 게시글의 ID
# requested_user_id: 요청을 보낸 사용자의 ID (비로그인 시 None)
def get_post_detail(post_id, requested_user_id=None):
    # DB 연결 객체 가져오기
    conn = get_connection()
    if not conn:
        return {"status": "FAILURE", "message": "DB 연결 실패"}

    try:
        cursor = conn.cursor()
        
        # 0. 게시글 존재 여부 및 권한 체크를 위한 기본 정보 조회
        check_query = "SELECT user_id, private FROM posts WHERE post_id = %s"
        cursor.execute(check_query, (post_id,))
        result = cursor.fetchone()
        
        if not result:
            # 게시글이 존재하지 않는 경우
            return {"status": "FAILURE", "message": "게시글을 찾을 수 없습니다."}
            
        post_owner_id, is_private = result
        is_private = bool(is_private)
        
        # 1. Private 게시글 권한 확인
        # 비공개(private=True)인 경우, 요청자가 작성자 본인이 아니라면 접근 거부
        if is_private and (requested_user_id is None or post_owner_id != requested_user_id):
            return {"status": "FAILURE", "message": "비공개 게시글이거나, 접근 권한이 없습니다."}

        # 2. 조회수 증가 (접근 권한 확인 후 증가)
        update_view_count_query = "UPDATE posts SET view_count = view_count + 1 WHERE post_id = %s"
        cursor.execute(update_view_count_query, (post_id,))
        # 조회수 증가는 즉시 DB에 반영
        conn.commit() 

        # 3. 상세 정보 조회 (증가된 view_count 포함)
        select_query = """
        SELECT 
            p.post_id, p.title, p.body, p.created_at, p.like_count, p.comment_count, 
            p.view_count, p.pinned, p.private, COALESCE(pr.name, '익명') AS user_name, p.user_id
        FROM posts p
        LEFT JOIN profiles pr ON p.user_id = pr.user_id
        WHERE p.post_id = %s
        """
        cursor.execute(select_query, (post_id,))
        row = cursor.fetchone()
            
        # 조회된 결과를 딕셔너리로 변환
        post_detail = {
            "post_id": row[0],
            "title": row[1],
            "body": row[2],
            "created_at": row[3].strftime("%Y-%m-%d %H:%M:%S") if isinstance(row[3], datetime) else str(row[3]),
            "like_count": row[4],
            "comment_count": row[5],
            "view_count": row[6],
            "pinned": bool(row[7]),
            "private": bool(row[8]),
            "user_name": row[9],
            "user_id": row[10]
        }
        
        return {"status": "SUCCESS", "post": post_detail}

    except mysql.connector.Error as e:
        # DB 오류 발생 시 롤백 (조회수 증가 포함)
        conn.rollback() 
        return {"status": "FAILURE", "message": f"DB 처리 중 오류 발생: {e}"}

    finally:
        # DB 연결 종료
        close_connection(conn)




# -------------------------- 4. 게시글 수정 (Update) --------------------------
# post_id: 수정할 게시글의 ID
# user_id: 요청을 보낸 사용자의 ID (권한 확인용)
# title, body, pinned, private: 수정할 내용
def update_post(post_id, user_id, title, body, pinned, private):
    # DB 연결 객체 가져오기
    conn = get_connection()
    if not conn:
        return {"status": "FAILURE", "message": "DB 연결 실패"}

    try:
        cursor = conn.cursor()
        
        # a. 권한 확인: 게시글 작성자 ID 조회
        check_query = "SELECT user_id FROM posts WHERE post_id = %s"
        cursor.execute(check_query, (post_id,))
        result = cursor.fetchone()

        if not result:
            # 게시글이 존재하지 않는 경우
            return {"status": "FAILURE", "message": "게시글을 찾을 수 없습니다."}
        
        post_owner_id = result[0]
        
        if post_owner_id != user_id:
            # 요청자 ID와 작성자 ID가 다르면 거부 (403 Forbidden)
            return {"status": "FAILURE", "message": "권한 없음"}
            
        # b. 게시글 수정 (title, body, pinned, private 필드 업데이트)
        update_query = """
        UPDATE posts 
        SET title = %s, body = %s, pinned = %s, private = %s 
        WHERE post_id = %s
        """
        cursor.execute(update_query, (title, body, pinned, private, post_id))
        
        # 변경 사항 DB에 확정
        conn.commit()
        return {"status": "SUCCESS", "message": "게시글이 성공적으로 수정되었습니다."}

    except mysql.connector.Error as e:
        # DB 오류 발생 시 롤백
        conn.rollback() 
        return {"status": "FAILURE", "message": f"DB 처리 중 오류 발생: {e}"}

    finally:
        # DB 연결 종료
        close_connection(conn)




# -------------------------- 5. 게시글 삭제 (Delete) --------------------------
# post_id: 삭제할 게시글의 ID
# user_id: 요청을 보낸 사용자의 ID (권한 확인용)
def delete_post(post_id, user_id):
    # DB 연결 객체 가져오기
    conn = get_connection()
    if not conn:
        return {"status": "FAILURE", "message": "DB 연결 실패"}

    try:
        cursor = conn.cursor()
        
        # a. 권한 확인: 게시글 작성자 ID 조회
        check_query = "SELECT user_id FROM posts WHERE post_id = %s"
        cursor.execute(check_query, (post_id,))
        result = cursor.fetchone()

        if not result:
            # 게시글이 존재하지 않는 경우
            return {"status": "FAILURE", "message": "게시글을 찾을 수 없습니다."}
        
        post_owner_id = result[0]
        
        if post_owner_id != user_id:
            # 요청자 ID와 작성자 ID가 다르면 거부 (403 Forbidden)
            return {"status": "FAILURE", "message": "권한 없음"}

        # b. 게시글 삭제 
        # (DB 스키마에 따라 좋아요/댓글 레코드는 자동 삭제됨)
        delete_query = "DELETE FROM posts WHERE post_id = %s"
        cursor.execute(delete_query, (post_id,))
        
        # 변경 사항 DB에 확정
        conn.commit()
        return {"status": "SUCCESS", "message": "게시글이 성공적으로 삭제되었습니다."}
        
    except mysql.connector.Error as e:
        # DB 오류 발생 시 롤백
        conn.rollback()
        return {"status": "FAILURE", "message": f"DB 처리 중 오류 발생: {e}"}

    finally:
        # DB 연결 종료
        close_connection(conn)