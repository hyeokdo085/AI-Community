CREATE SCHEMA IF NOT EXISTS ai_community DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
-- ai_community 라는 이름의 스키마 생성

-- 사용할 DB를 ai_community로 지정
USE ai_community; 

-- 1. 사용자 정보 테이블 생성 (users)
CREATE TABLE IF NOT EXISTS users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    role ENUM('user', 'admin') DEFAULT 'user'
);

-- 2. 사용자 프로필 테이블 생성 (profiles) - users 테이블의 id를 참조 (1:1 관계)
CREATE TABLE IF NOT EXISTS profiles (
    user_id INT PRIMARY KEY,
    name VARCHAR(30),
    bio VARCHAR(100),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- 3. 게시글 테이블 생성 (posts) - users 테이블의 id를 참조 (1:N 관계)
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
);

-- 4. 댓글 테이블 생성 (comments) - posts 및 users 테이블을 참조 (1:N 관계)
CREATE TABLE IF NOT EXISTS comments (
    comment_id INT PRIMARY KEY AUTO_INCREMENT,
    post_id INT NOT NULL,
    user_id INT NOT NULL,
    comment_body TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (post_id) REFERENCES posts(post_id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- 5. 좋아요 테이블 생성 (post_likes) - users 및 posts 테이블을 참조
CREATE TABLE IF NOT EXISTS post_likes (
    user_id INT NOT NULL,
    post_id INT NOT NULL,
    PRIMARY KEY (user_id, post_id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (post_id) REFERENCES posts(post_id)
);





