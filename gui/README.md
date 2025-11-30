# 🎨 AI Community - GUI 업그레이드

## 📦 포함된 파일

```
gui/
├── ai_service.py              # 버그 수정 (IndentationError 해결)
├── static/
│   ├── css/
│   │   └── main.css          # 사이버펑크 네온 테마
│   └── js/
│       └── chat.js           # 향상된 인터랙션 & 애니메이션
└── templates/
    ├── layout.html           # 테마 토글 추가
    ├── index.html            # 로그인/회원가입 페이지
    └── chat.html             # 채팅 페이지
```

## 🚀 설치 방법

### 1. 파일 복사

프로젝트 루트 디렉토리에서:

```bash
# ai_service.py 교체 (필수!)
copy gui\ai_service.py .

# static 폴더 교체
copy gui\static\css\main.css static\css\
copy gui\static\js\chat.js static\js\

# templates 폴더 교체
copy gui\templates\*.html templates\
```

### 2. 서버 실행

```bash
python server_main.py
```

### 3. 브라우저 접속

```
http://localhost:5000
```

## ✨ 새로운 기능

### 🎨 디자인
- **사이버펑크 네온 테마**: 형광 효과와 그리드 애니메이션
- **다크/라이트 모드**: 🌙/☀️ 버튼으로 전환 가능
- **3D 호버 효과**: 카드와 버튼에 입체감
- **파티클 배경**: 떠다니는 네온 파티클

### ⚡ 애니메이션
- **타이핑 효과**: AI 응답이 실시간으로 타이핑됨
- **메시지 슬라이드**: 부드러운 등장 애니메이션
- **네온 글로우**: 모든 요소에 빛나는 효과
- **로딩 인디케이터**: AI 응답 대기 중 점 3개 애니메이션

### ⌨️ 단축키
- `Alt + T`: 다크/라이트 모드 전환
- `Alt + R`: 채팅 기록 새로고침
- `Shift + Enter`: 줄바꿈
- `Enter`: 메시지 전송

### 🎯 사용성 개선
- **자동 스크롤**: 새 메시지가 오면 자동으로 하단으로
- **자동 새로고침**: 5초마다 채팅 기록 업데이트
- **반응형 디자인**: 모바일, 태블릿, 데스크톱 완벽 지원
- **접근성**: 키보드 네비게이션, ARIA 레이블

## 🔧 기술 스택

- **CSS**: CSS Variables, Flexbox, Grid, Animations
- **JavaScript**: ES6+, Fetch API, Intersection Observer
- **폰트**: Orbitron (디스플레이), Inter (본문)
- **테마**: 다크 모드 기본, 로컬 스토리지 저장

## ⚠️ 중요 사항

### 호환성
- ✅ 기존 `server_API.py` 완벽 호환
- ✅ `db_utils`, `db_config` 연동 유지
- ✅ JSON 프로토콜 (`chat_protocol.py`) 준수
- ✅ 모든 백엔드 로직 변경 없음

### Gemini API
- API 키 설정: `ai_service.py` 25번 줄
- 또는 환경 변수: `GEMINI_API_KEY`
- 무료 플랜: 분당 15개, 일일 1500개 요청

## 📸 스크린샷

### 다크 모드 (기본)
- 사이버펑크 네온 효과
- 청록색 + 마젠타 + 노랑 조합
- 그리드 배경 애니메이션

### 라이트 모드
- 깔끔한 흰색 배경
- 파란색 + 핑크 강조색
- 부드러운 그림자 효과

## 🎉 사용 팁

1. **처음 접속 시**: 회원가입 후 로그인
2. **AI 채팅**: 메시지 입력 후 Enter (Shift+Enter로 줄바꿈)
3. **테마 전환**: 상단 우측 🌙/☀️ 버튼 또는 `Alt + T`
4. **새로고침**: 🔄 버튼 또는 `Alt + R`

## 🛠️ 문제 해결

### 서버가 실행되지 않는 경우
```bash
# 캐시 삭제
rmdir /s /q __pycache__

# 다시 실행
python server_main.py
```

### API 키 오류
- Google AI Studio에서 새 API 키 발급
- https://aistudio.google.com/app/apikey

## 👥 팀 통합

이 GUI는 기존 팀 프로젝트 구조와 완벽하게 호환됩니다:
- `db_*` 파일: 영향 없음
- `server_*` 파일: 영향 없음
- `client_*` 파일: 영향 없음
- `test_*` 파일: 영향 없음

---

**Made with ❤️ for AI Community Team**

v1.0.0 - 2025.11.29





