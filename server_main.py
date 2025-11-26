# server_main.py
# 메인 어플리케이션 실행
# Flask 서버 구동, API 테스트

from server_API import community_API

# 서버 실행 부분
if __name__ == '__main__':
    # 코드 수정 시 서버가 자동으로 재시작되도록 debug 모드 활성화
    community_API.run(debug=True)