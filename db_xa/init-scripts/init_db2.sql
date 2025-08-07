-- 2번 DB 초기화 스크립트
CREATE TABLE IF NOT EXISTS user_profile (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    phone VARCHAR(20),
    address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id)
);

-- 테스트용 초기 데이터
INSERT INTO user_profile (user_id, first_name, last_name, phone, address) VALUES 
(1, 'John', 'Doe', '010-1234-5678', 'Seoul, Korea'),
(2, 'Jane', 'Smith', '010-9876-5432', 'Busan, Korea');