"""
WebSocket 기반 채팅 서버
순수 소켓 모듈을 사용한 실시간 채팅 서버
"""

import socket
import json
import threading
import uuid
import hashlib
import base64
import struct
from datetime import datetime, timezone
from chat_protocol import validate_packet, build_packet, ProtocolError
from ai_service import ai_service

# 서버 설정
HOST = '127.0.0.1'
PORT = 9999
MAX_CLIENTS = 50

# 연결된 클라이언트 관리
clients = {}  # {socket: {"email": str, "user_id": int}}
clients_lock = threading.Lock()

# 채팅 히스토리
chat_history = []


def websocket_handshake(client_socket):
    """WebSocket 핸드셰이크 처리"""
    try:
        # HTTP 요청 읽기
        request = b""
        while b"\r\n\r\n" not in request:
            chunk = client_socket.recv(1024)
            if not chunk:
                return False
            request += chunk
        
        # Sec-WebSocket-Key 추출
        request_str = request.decode('utf-8')
        lines = request_str.split('\r\n')
        
        websocket_key = None
        for line in lines:
            if line.startswith('Sec-WebSocket-Key:'):
                websocket_key = line.split(':', 1)[1].strip()
                break
        
        if not websocket_key:
            return False
        
        # WebSocket Accept 키 생성
        magic_string = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
        accept_key = base64.b64encode(
            hashlib.sha1((websocket_key + magic_string).encode()).digest()
        ).decode()
        
        # 핸드셰이크 응답
        response = (
            "HTTP/1.1 101 Switching Protocols\r\n"
            "Upgrade: websocket\r\n"
            "Connection: Upgrade\r\n"
            f"Sec-WebSocket-Accept: {accept_key}\r\n"
            "\r\n"
        )
        
        client_socket.sendall(response.encode('utf-8'))
        return True
    
    except Exception as e:
        print(f"[ERROR] WebSocket 핸드셰이크 실패: {e}")
        return False


def send_websocket_frame(client_socket, data):
    """WebSocket 프레임 인코딩하여 전송"""
    try:
        message = data.encode('utf-8')
        length = len(message)
        
        # 프레임 헤더 생성
        frame = bytearray()
        frame.append(0x81)  # FIN=1, opcode=1 (텍스트)
        
        if length <= 125:
            frame.append(length)
        elif length <= 65535:
            frame.append(126)
            frame.extend(struct.pack(">H", length))
        else:
            frame.append(127)
            frame.extend(struct.pack(">Q", length))
        
        frame.extend(message)
        client_socket.sendall(bytes(frame))
        return True
    except Exception as e:
        print(f"[ERROR] WebSocket 프레임 전송 실패: {e}")
        return False


def receive_websocket_frame(client_socket):
    """WebSocket 프레임 디코딩"""
    try:
        # 첫 2바이트 읽기
        header = client_socket.recv(2)
        if len(header) < 2:
            return None
        
        # 페이로드 길이 파싱
        payload_length = header[1] & 0x7F
        
        if payload_length == 126:
            extended = client_socket.recv(2)
            payload_length = struct.unpack(">H", extended)[0]
        elif payload_length == 127:
            extended = client_socket.recv(8)
            payload_length = struct.unpack(">Q", extended)[0]
        
        # 마스킹 키 읽기
        masking_key = client_socket.recv(4)
        
        # 페이로드 읽기
        payload = bytearray()
        while len(payload) < payload_length:
            chunk = client_socket.recv(payload_length - len(payload))
            if not chunk:
                break
            payload.extend(chunk)
        
        # 언마스킹
        unmasked = bytearray()
        for i in range(len(payload)):
            unmasked.append(payload[i] ^ masking_key[i % 4])
        
        return unmasked.decode('utf-8')
    
    except Exception as e:
        print(f"[ERROR] WebSocket 프레임 수신 실패: {e}")
        return None


def broadcast_message(packet_dict, exclude_socket=None):
    """모든 클라이언트에게 메시지 브로드캐스트"""
    message = json.dumps(packet_dict, ensure_ascii=False)
    
    with clients_lock:
        disconnected = []
        for client_socket, client_info in clients.items():
            if client_socket != exclude_socket:
                try:
                    if client_info.get("is_websocket", False):
                        send_websocket_frame(client_socket, message)
                    else:
                        # 일반 TCP 소켓 (터미널 클라이언트)
                        client_socket.sendall((message + "\n").encode('utf-8'))
                except Exception as e:
                    print(f"[ERROR] 클라이언트 전송 실패: {e}")
                    disconnected.append(client_socket)
        
        # 연결이 끊긴 클라이언트 제거
        for sock in disconnected:
            if sock in clients:
                del clients[sock]


def handle_client(client_socket, address):
    """개별 클라이언트 처리"""
    print(f"[NEW CONNECTION] {address} 연결됨")
    
    # WebSocket 핸드셰이크 시도
    is_websocket = websocket_handshake(client_socket)
    
    client_info = {
        "email": f"guest_{address[1]}", 
        "user_id": 0,
        "is_websocket": is_websocket
    }
    
    with clients_lock:
        clients[client_socket] = client_info
    
    if is_websocket:
        print(f"[WebSocket] {address} WebSocket 연결 완료")
    else:
        print(f"[TCP] {address} 일반 TCP 소켓 연결")
    
    # 환영 메시지
    welcome_packet = build_packet(
        sender="SYSTEM",
        body=f"채팅 서버에 오신 것을 환영합니다! (연결: {address})",
        message_type="SYSTEM",
        metadata={"connection_time": datetime.now(timezone.utc).isoformat()}
    )
    
    try:
        welcome_msg = json.dumps(welcome_packet, ensure_ascii=False)
        if is_websocket:
            send_websocket_frame(client_socket, welcome_msg)
        else:
            client_socket.sendall((welcome_msg + "\n").encode('utf-8'))
    except Exception as e:
        print(f"[ERROR] 환영 메시지 전송 실패: {e}")
    
    buffer = ""
    
    try:
        while True:
            # 데이터 수신
            if is_websocket:
                # WebSocket 프레임 수신
                line = receive_websocket_frame(client_socket)
                if not line:
                    break
                line = line.strip()
            else:
                # 일반 TCP 소켓 (터미널 클라이언트)
                data = client_socket.recv(4096).decode('utf-8')
                if not data:
                    break
                
                buffer += data
                
                # 줄바꿈으로 구분된 메시지 처리
                if '\n' not in buffer:
                    continue
                    
                line, buffer = buffer.split('\n', 1)
                line = line.strip()
            
            if not line:
                continue
            
            try:
                # JSON 파싱
                raw_packet = json.loads(line)
                
                # 프로토콜 검증
                normalized = validate_packet(raw_packet)
                
                # 서버 측에서 sender 정보 덮어쓰기 (보안)
                normalized["header"]["sender"] = client_info["email"]
                normalized["payload"]["metadata"]["user_id"] = client_info["user_id"]
                
                # 히스토리에 추가
                chat_history.append(normalized)
                
                print(f"[MESSAGE] {client_info['email']}: {normalized['payload']['body']}")
                
                # 모든 클라이언트에게 브로드캐스트
                broadcast_message(normalized, exclude_socket=None)
                
                # AI 응답 생성 (필요시)
                if normalized["payload"]["metadata"].get("ask_ai", False):
                    user_message = normalized["payload"]["body"]
                    history_texts = [
                        msg["payload"]["body"] 
                        for msg in chat_history[-10:] 
                        if msg["header"]["message_type"] == "CHAT"
                    ]
                    
                    ai_response = ai_service.reply(history_texts, user_message)
                    
                    ai_packet = build_packet(
                        sender="AI-Assistant",
                        body=ai_response,
                        message_type="AI",
                        channel=normalized["header"]["channel"],
                        metadata={
                            "source": "gemini" if ai_service.available else "fallback",
                            "in_reply_to": normalized["header"]["message_id"]
                        }
                    )
                    
                    chat_history.append(ai_packet)
                    broadcast_message(ai_packet)
                    
                    print(f"[AI] {ai_response[:50]}...")
            
            except ProtocolError as e:
                error_packet = build_packet(
                    sender="SYSTEM",
                    body=f"프로토콜 오류: {str(e)}",
                    message_type="SYSTEM",
                    metadata={"error": True}
                )
                error_msg = json.dumps(error_packet, ensure_ascii=False)
                if is_websocket:
                    send_websocket_frame(client_socket, error_msg)
                else:
                    client_socket.sendall((error_msg + "\n").encode('utf-8'))
                print(f"[PROTOCOL ERROR] {e}")
            
            except json.JSONDecodeError as e:
                print(f"[JSON ERROR] {e}: {line[:100]}")
            
            except Exception as e:
                print(f"[ERROR] 메시지 처리 중 오류: {e}")
    
    except Exception as e:
        print(f"[ERROR] 클라이언트 처리 중 오류: {e}")
    
    finally:
        # 연결 종료
        with clients_lock:
            if client_socket in clients:
                del clients[client_socket]
        
        # 퇴장 메시지 브로드캐스트
        leave_packet = build_packet(
            sender="SYSTEM",
            body=f"{client_info['email']}님이 채팅방을 나갔습니다.",
            message_type="SYSTEM",
            metadata={"user_left": True}
        )
        broadcast_message(leave_packet)
        
        client_socket.close()
        print(f"[DISCONNECTED] {address} 연결 종료")


def start_server():
    """소켓 채팅 서버 시작"""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server_socket.bind((HOST, PORT))
        server_socket.listen(MAX_CLIENTS)
        
        print("=" * 60)
        print(f"🚀 WebSocket 채팅 서버 시작")
        print(f"📡 주소: {HOST}:{PORT}")
        print(f"👥 최대 클라이언트: {MAX_CLIENTS}")
        print(f"🤖 AI 서비스: {'활성화' if ai_service.available else '비활성화 (fallback 모드)'}")
        print("=" * 60)
        
        while True:
            client_socket, address = server_socket.accept()
            
            # 새 클라이언트를 별도 스레드에서 처리
            client_thread = threading.Thread(
                target=handle_client,
                args=(client_socket, address),
                daemon=True
            )
            client_thread.start()
            
            print(f"[ACTIVE CONNECTIONS] 현재 {len(clients)}명 접속 중")
    
    except KeyboardInterrupt:
        print("\n[SHUTDOWN] 서버 종료 중...")
    
    except Exception as e:
        print(f"[ERROR] 서버 오류: {e}")
    
    finally:
        server_socket.close()
        print("[SHUTDOWN] 서버가 종료되었습니다.")


if __name__ == "__main__":
    start_server()

