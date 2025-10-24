import socket, json, time, threading, random

# === Proxy configuration ===
# Proxy1 = LOSS path
# Proxy2 = DELAY path
proxy_loss = ('192.168.4.251', 5406)
proxy_delay = ('192.168.4.251', 5408)
client_ack_port = 5407

# === Transmission parameters ===
N = 10000
timeout = 0.3
window_size = 100
max_wait = 60

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(('192.168.4.250', 0))
s.settimeout(0.05)

ack_set = set()
lock = threading.Lock()
retransmit_count = 0
last_ack_time = time.time()

# === Thread to receive ACKs ===
def listen_ack():
    while True:
        try:
            data, _ = s.recvfrom(4096)
            msg = json.loads(data.decode('utf-8'))
            if msg.get("type") == "ack":
                with lock:
                    ack_set.add(msg["id"])
        except socket.timeout:
            continue

threading.Thread(target=listen_ack, daemon=True).start()

print(f"[SERVER] Start sending {N} packets (Path1=LOSS, Path2=DELAY)")

start_time = time.time()
base = 1

# Use bias to prefer delay path for retransmissions
bias_delay = 0.5  # probability of using delay path in normal transmission

while base <= N:
    for i in range(base, min(base + window_size, N + 1)):
        if i in ack_set:
            continue

        # Choose random path for first transmission
        if random.random() > bias_delay:
            path = 'LOSS'
            target = proxy_loss
        else:
            path = 'DELAY'
            target = proxy_delay

        pkt = json.dumps({
            "id": i,
            "send_time": time.time(),
            "path": path
        })
        s.sendto(pkt.encode(), target)

    time.sleep(timeout)

    # Check missing ACKs and retransmit
    with lock:
        pending = [p for p in range(base, base + window_size) if p not in ack_set and p <= N]
    if pending:
        for pid in pending:
            retransmit_count += 1
            # Retransmit using DELAY path to improve reliability
            pkt = json.dumps({
                "id": pid,
                "send_time": time.time(),
                "path": "RETX-DELAY"
            })
            s.sendto(pkt.encode(), proxy_delay)

    # Slide window forward
    while base in ack_set:
        base += 1
        last_ack_time = time.time()

    # Stop if too long no ACK
    if time.time() - last_ack_time > max_wait:
        print(f"[TIMEOUT] No new ACKs for {max_wait}s, stop sending.")
        break

duration = time.time() - start_time
print(f"\n[SERVER DONE] Sent {N} packets in {duration:.2f}s.")
print(f"Retransmissions: {retransmit_count}")
print(f"Effective retransmit ratio: {retransmit_count / N:.2%}")
s.close()
