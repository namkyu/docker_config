import socket, time

HOST, PORT = "0.0.0.0", 5000
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen(1)
    conn, addr = s.accept()
    data = conn.recv(4096)
    print(f"accepted {addr}, got {data!r}")

    # 서버는 이 시점에서 FIN을 받으면 즉시 ACK 응답
    time.sleep(300)  # 서버는 FIN을 보내지 않고 연결을 붙잡고 있는 구간
    # 이 시간 동안 클라이언트는 FIN_WAIT_2 상태 유지

    conn.close()
    # 서버가 close() 호출 후 FIN 전송
    # 클라이언트가 이 FIN을 받고 마지막 ACK 응답 후 TIME_WAIT 상태로 전환
