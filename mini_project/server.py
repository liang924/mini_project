import socket, time, random, json

proxy1_ip, proxy1_port = '192.168.92.1', 5406   # Proxy1 
proxy2_ip, proxy2_port = '192.168.92.1', 5408   # Proxy2 

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

N = 100000
for i in range(1, N+1):
    path = random.choice([1, 2])  # 隨機選路徑
    send_t = time.time()
    msg = {
        "id": i,
        "path": path,
        "timestamp": send_t,
    }
    encoded = json.dumps(msg).encode('utf-8')

    if path == 1:
        s.sendto(encoded, (proxy1_ip, proxy1_port))
    else:
        s.sendto(encoded, (proxy2_ip, proxy2_port))

    print(f"Packet {i:06d} sent via Path{path} at t = {send_t:.6f}")
    time.sleep(0.01)

