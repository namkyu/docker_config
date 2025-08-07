-- 1번 DB 초기화 스크립트
CREATE TABLE IF NOT EXISTS user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_username (username)
);

-- 테스트용 초기 데이터
INSERT INTO user (username, email) VALUES 
('testuser1', 'test1@example.com'),
('testuser2', 'test2@example.com');