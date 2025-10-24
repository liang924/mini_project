import socket
import random
import time
import json

client_ip = '192.168.92.1'      # UDP Client
client_port = 5407
proxy_ip = '192.168.92.1'       # This proxy's IP
proxy_port = 5406                # LOSS path

loss_probability = 0.10          # 10% packet loss
timeout_sec = 5                  # End if no packet for 5 sec
total_received = 0
total_lost = 0
N = 100000

# === Create UDP socket ===
c = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
c.bind((proxy_ip, proxy_port))
c.settimeout(timeout_sec)

print(f"[Proxy-Loss] Ready at {proxy_ip}:{proxy_port} | Loss={loss_probability*100:.1f}%")

start_time = time.time()

while True:
    try:
        recv_data, sender_addr = c.recvfrom(65535)
        message = recv_data.decode('utf-8')

        # === Parse JSON packet ===
        try:
            msg = json.loads(message)
            flag = msg.get("id", -1)
        except Exception:
            continue  # skip invalid packet

        total_received += 1

        # === Simulate 10% loss ===
        if random.random() <= loss_probability:
            total_lost += 1
            print(f"[Proxy-Loss] Packet {flag:05d} DROPPED")
            continue  # Don't forward

        # === Forward to client ===
        c.sendto(recv_data, (client_ip, client_port))

    except socket.timeout:
        print(f"\n[Proxy-Loss] No packets received for {timeout_sec}s → Ending session.")
        break

    except KeyboardInterrupt:
        print("\n[Proxy-Loss] Stopped manually.")
        break

    except Exception as e:
        print("[Proxy-Loss] Error:", e)
        break

# === Statistics ===
elapsed = time.time() - start_time
loss_rate = total_lost * 100 / max(1, total_received)

print("\n================ Statistics ================")
print(f"Total packets received : {total_received}")
print(f"Lost packets           : {total_lost}")
print(f"Effective loss rate    : {loss_rate:.2f}%")
print(f"Run time               : {elapsed:.2f}s")
print("============================================")

c.close()
