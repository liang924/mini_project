import socket

proxy_ip = '192.168.4.251'
proxy_listen_port = 5408
client_ip = '192.168.4.248'
client_port = 5407

proxy_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
proxy_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
proxy_server.bind((proxy_ip, proxy_listen_port))
proxy_server.listen(1)

print(f"[TCP PROXY] Listening on {proxy_ip}:{proxy_listen_port} ...")
server_conn, server_addr = proxy_server.accept()
print(f"[CONNECTED] Server connected from {server_addr}")

proxy_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
proxy_client.connect((client_ip, client_port))
print(f"[CONNECTED] Proxy connected to Client at {client_ip}:{client_port}")
print("[INFO] Ready to forward packets.\n")

try:
    buffer = ""
    while True:
        data = server_conn.recv(65535)
        if not data:
            print("[FIN] Server closed connection.")
            break

        buffer += data.decode('utf-8', errors='ignore')
        while '\n' in buffer:
            line, buffer = buffer.split('\n', 1)
            if not line.strip():
                continue
            print("Forwarding:", line)
            proxy_client.sendall((line + '\n').encode('utf-8'))

            if line.strip().startswith("Packet 100 "):
                print("[FIN] All packets forwarded.")
                raise StopIteration

except StopIteration:
    pass
except ConnectionResetError:
    print("[ERROR] Connection reset by peer.")
except Exception as e:
    print("[ERROR]", e)
finally:
    server_conn.close()
    proxy_client.close()
    proxy_server.close()
    print("[CLOSED] TCP Proxy sockets closed.")


