# 테스트 가이드

## ✅ 현재까지 완료된 테스트

### 1. 코드 구조 및 문법 테스트 (완료)
- ✅ 모든 모듈 import 성공
- ✅ 채팅 프로토콜 패킷 생성/검증 정상 작동
- ✅ AI 서비스 응답 생성 정상 작동 (fallback 모드)
- ✅ Flask 앱 구조 정상 (9개 라우트 등록됨)

### 2. 등록된 API 엔드포인트
- `GET /` - 로그인/회원가입 페이지
- `GET /chat` - 채팅 페이지
- `POST /login` - 로그인
- `POST /register` - 회원가입
- `POST /logout` - 로그아웃
- `GET /session` - 세션 상태 확인
- `GET /api/chat/history` - 채팅 히스토리 조회
- `POST /api/chat/send` - 채팅 메시지 전송

## 🔧 다음 단계: MySQL 서버 시작 후 테스트

### 1. MySQL 서버 시작
Windows에서 MySQL 서버를 시작하는 방법:
- **방법 1**: MySQL Workbench에서 서버 시작
- **방법 2**: 서비스 관리자에서 MySQL 서비스 시작
- **방법 3**: 명령 프롬프트에서 `net start MySQL` (관리자 권한 필요)

### 2. DB 스키마 생성
```bash
python setup_database.py
```

이 스크립트는 다음을 생성합니다:
- `ai_community` 스키마
- `users` 테이블 (사용자 정보)
- `profiles` 테이블 (사용자 프로필)
- `posts` 테이블 (게시글)
- `comments` 테이블 (댓글)
- `post_likes` 테이블 (좋아요)

### 3. 로그인/회원가입 기능 테스트
```bash
python test_login_register.py
```

### 4. 웹 서버 실행 및 브라우저 테스트
```bash
python server_main.py
```

서버가 시작되면 브라우저에서 `http://127.0.0.1:5000` 접속

## 📝 테스트 체크리스트

### DB 연결 테스트
- [ ] MySQL 서버 실행 확인
- [ ] `python db_test.py` 실행 성공
- [ ] `python setup_database.py` 실행 성공

### 기능 테스트
- [ ] 회원가입 테스트
- [ ] 중복 이메일 방지 테스트
- [ ] 로그인 성공 테스트
- [ ] 로그인 실패 테스트 (잘못된 비밀번호)
- [ ] 웹 UI 접속 테스트
- [ ] 채팅 메시지 전송 테스트
- [ ] AI 응답 생성 테스트

### 환경 변수 설정 (선택사항)
- `OPENAI_API_KEY`: OpenAI API 키 (AI 응답 활성화)
- `FLASK_SECRET_KEY`: 세션 암호화 키 (기본값: "dev-secret")

## 🐛 문제 해결

### MySQL 연결 오류
- 오류: `Can't connect to MySQL server on '127.0.0.1:3306'`
- 해결: MySQL 서버가 실행 중인지 확인
- `db_config.py`의 연결 정보 확인 (host, port, user, password, database)

### 모듈 import 오류
- 필요한 패키지 설치: `pip install -r requirements.txt`
- 또는 개별 설치: `pip install flask flask-bcrypt mysql-connector-python openai`





