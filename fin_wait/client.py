import socket
import time

HOST, PORT = "127.0.0.1", 5000
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.sendall(b"hello")
    time.sleep(2)  # 서버가 데이터 받도록 잠시 대기
    s.shutdown(socket.SHUT_WR)  # 클라이언트가 먼저 FIN 전송
    time.sleep(60)  # 서버가 FIN을 보내지 않는 동안 FIN_WAIT_2 상태 유지
    s.close() # close() 후 TIME_WAIT 상태로 진입
