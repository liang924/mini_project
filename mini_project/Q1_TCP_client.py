import socket
import time

client_ip = '192.168.4.248'
client_port = 5407

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
client.bind((client_ip, client_port))
client.listen(1)

print(f"[TCP CLIENT] Listening on {client_ip}:{client_port} ...")

proxy_conn, proxy_addr = client.accept()
print(f"[CONNECTED] Proxy connected from {proxy_addr}")

buffer = ""
while True:
    data = proxy_conn.recv(65535)
    if not data:
        print("[FIN] Proxy closed connection.")
        break

    buffer += data.decode('utf-8', errors='ignore')
    while '\n' in buffer:
        line, buffer = buffer.split('\n', 1)
        if not line.strip():
            continue

        parts = line.split("t = ")
        try:
            send_time = float(parts[1]) if len(parts) > 1 else 0.0
        except ValueError:
            continue

        recv_time = time.time()
        delay = recv_time - send_time
        print(f"{line} | recv_time = {recv_time:.5f} | delay = {delay:.5f} sec")

        if "Packet 100" in line:
            print("[COMPLETE] All packets received. Closing connection.")
            proxy_conn.close()
            client.close()
            print("[CLOSED] TCP Client socket closed.")
            exit()





