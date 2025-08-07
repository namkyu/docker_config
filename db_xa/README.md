# XA 분산 트랜잭션 테스트 환경

MySQL 2대를 사용한 XA (eXtended Architecture) 분산 트랜잭션 테스트 환경입니다.

## 구성

- **DB1 (mysql-db1)**: `localhost:3306` - `testdb1` 데이터베이스, `user` 테이블
- **DB2 (mysql-db2)**: `localhost:3307` - `testdb2` 데이터베이스, `user_profile` 테이블

## 사용법

### 1. 환경 시작
```bash
# Windows
start_docker_compose.bat

# Linux/Mac
docker-compose up -d
```

### 2. Python 의존성 설치
```bash
pip install -r requirements.txt
```

### 3. XA 트랜잭션 테스트 실행
```bash
python test_xa_transaction.py
```

### 4. 환경 중지
```bash
# Windows
stop_docker_compose.bat

# Linux/Mac
docker-compose down
```

## 테스트 시나리오

### 1. 성공 케이스 (Commit)
- DB1의 `user` 테이블에 새 사용자 삽입
- DB2의 `user_profile` 테이블에 해당 사용자의 프로필 삽입
- 2 Phase Commit으로 두 작업 모두 성공 시 커밋

### 2. 실패 케이스 (Rollback)
- DB1의 `user` 테이블에 새 사용자 삽입 (성공)
- DB2의 `user_profile` 테이블에 의도적으로 실패하는 작업 수행
- 한 쪽이 실패하면 양쪽 모두 롤백

## XA 트랜잭션 명령어

### 기본 XA 명령어
```sql
XA START 'xid'      -- XA 트랜잭션 시작
XA END 'xid'        -- XA 트랜잭션 종료 (작업 완료)
XA PREPARE 'xid'    -- Phase 1: 준비 단계
XA COMMIT 'xid'     -- Phase 2: 커밋
XA ROLLBACK 'xid'   -- Phase 2: 롤백
XA RECOVER          -- 준비된 XA 트랜잭션 목록 조회
```

### 수동 테스트 (MySQL 클라이언트)
```bash
# DB1 접속
mysql -h localhost -P 3306 -u root -p

# DB2 접속
mysql -h localhost -P 3307 -u root -p
```

## 파일 구조
```
db_xa/
├── docker-compose.yml          # Docker Compose 설정
├── init-scripts/
│   ├── init_db1.sql           # DB1 초기화 스크립트
│   └── init_db2.sql           # DB2 초기화 스크립트
├── test_xa_transaction.py     # XA 트랜잭션 테스트 스크립트
├── requirements.txt           # Python 의존성
├── start_docker_compose.bat   # 시작 배치 파일
└── stop_docker_compose.bat    # 중지 배치 파일
```