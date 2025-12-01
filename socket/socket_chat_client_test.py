"""
터미널 기반 소켓 채팅 클라이언트 (테스트용)
브라우저 없이 순수 Python으로 채팅 서버에 연결
"""

import socket
import json
import threading
import sys
from datetime import datetime, timezone


HOST = '127.0.0.1'
PORT = 9999


def receive_messages(client_socket):
    """서버로부터 메시지 수신 (별도 스레드)"""
    buffer = ""
    
    try:
        while True:
            data = client_socket.recv(4096).decode('utf-8')
            if not data:
                print("\n[연결 종료] 서버와의 연결이 끊어졌습니다.")
                break
            
            buffer += data
            
            # 줄바꿈으로 구분된 메시지 처리
            while '\n' in buffer:
                line, buffer = buffer.split('\n', 1)
                line = line.strip()
                
                if not line:
                    continue
                
                try:
                    packet = json.loads(line)
                    display_message(packet)
                except json.JSONDecodeError as e:
                    print(f"[오류] JSON 파싱 실패: {e}")
    
    except Exception as e:
        print(f"\n[오류] 수신 중 에러: {e}")
    finally:
        sys.exit(0)


def display_message(packet):
    """수신한 메시지를 보기 좋게 출력"""
    header = packet.get("header", {})
    payload = packet.get("payload", {})
    
    sender = header.get("sender", "Unknown")
    msg_type = header.get("message_type", "CHAT")
    timestamp = header.get("timestamp", "")
    body = payload.get("body", "")
    
    # 시간 포맷팅
    try:
        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        time_str = dt.strftime("%H:%M:%S")
    except:
        time_str = ""
    
    # 메시지 타입에 따라 색상/아이콘 변경
    if msg_type == "SYSTEM":
        icon = "📢"
        color = "\033[93m"  # 노란색
    elif msg_type == "AI":
        icon = "🤖"
        color = "\033[96m"  # 청록색
    else:
        icon = "💬"
        color = "\033[92m"  # 초록색
    
    reset = "\033[0m"
    
    print(f"\n{color}{icon} [{time_str}] {sender}{reset}")
    print(f"   {body}")
    print(f"{'─' * 60}")


def build_packet(sender, body, ask_ai=False):
    """채팅 프로토콜 패킷 생성"""
    return {
        "header": {
            "version": "1.0",
            "message_type": "CHAT",
            "message_id": str(id(body)),  # 간단한 ID 생성
            "sender": sender,
            "channel": "lobby",
            "timestamp": datetime.now(timezone.utc).isoformat()
        },
        "payload": {
            "body": body,
            "metadata": {
                "ask_ai": ask_ai,
                "user_id": 0
            }
        }
    }


def send_message(client_socket, sender, message, ask_ai):
    """메시지 전송"""
    try:
        packet = build_packet(sender, message, ask_ai)
        message_json = json.dumps(packet, ensure_ascii=False) + "\n"
        client_socket.sendall(message_json.encode('utf-8'))
        print(f"[전송 완료] '{message[:30]}...'")
    except Exception as e:
        print(f"[오류] 전송 실패: {e}")


def main():
    """메인 실행 함수"""
    print("=" * 60)
    print("🚀 소켓 채팅 클라이언트 (터미널 버전)")
    print("=" * 60)
    
    # 사용자 이름 입력
    user_name = input("📝 사용자 이름을 입력하세요: ").strip()
    if not user_name:
        user_name = "Guest"
    
    print(f"\n👋 안녕하세요, {user_name}님!")
    print(f"🔌 서버 연결 중... ({HOST}:{PORT})")
    
    # 서버 연결
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((HOST, PORT))
        print("✅ 서버 연결 성공!\n")
    except Exception as e:
        print(f"❌ 서버 연결 실패: {e}")
        print(f"💡 서버가 실행 중인지 확인하세요: python socket_chat_server.py")
        return
    
    # 수신 스레드 시작
    receive_thread = threading.Thread(
        target=receive_messages,
        args=(client_socket,),
        daemon=True
    )
    receive_thread.start()
    
    print("\n" + "=" * 60)
    print("💡 사용 방법:")
    print("   - 메시지 입력 후 Enter로 전송")
    print("   - '@ai'로 시작하면 AI 응답 요청")
    print("   - '/quit' 또는 '/exit'로 종료")
    print("=" * 60)
    print()
    
    # 메시지 입력 루프
    try:
        while True:
            message = input(f"\n💭 메시지 입력 > ").strip()
            
            if not message:
                continue
            
            # 종료 명령어 확인
            if message.lower() in ['/quit', '/exit', '/q']:
                print("\n👋 채팅방을 나갑니다...")
                break
            
            # AI 응답 요청 확인
            ask_ai = message.startswith('@ai')
            if ask_ai:
                message = message[3:].strip()  # @ai 제거
                print("🤖 AI 응답을 요청합니다...")
            
            # 메시지 전송
            send_message(client_socket, user_name, message, ask_ai)
    
    except KeyboardInterrupt:
        print("\n\n👋 Ctrl+C 감지. 종료합니다...")
    
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
    
    finally:
        client_socket.close()
        print("🔌 연결이 종료되었습니다.")


if __name__ == "__main__":
    main()




