import socket
import time

proxy_ip = '192.168.4.251'
proxy_port = 5408

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

print(f"[TCP SERVER] Connecting to Proxy at {proxy_ip}:{proxy_port} ...")
server.connect((proxy_ip, proxy_port))
print("[CONNECTED] TCP connection established with Proxy.\n")

for i in range(1, 101):
    try:
        message = f"Packet {i:3d} sended at t = {time.time():.5f}\n"
        print(message.strip())
        server.sendall(message.encode('utf-8'))
        time.sleep(0.01)
    except BrokenPipeError:
        print("[ERROR] Broken pipe — Proxy closed connection early.")
        break

print("\n[FIN] All packets sent. Closing connection.")
server.close()
print("[CLOSED] TCP Server socket closed.")
