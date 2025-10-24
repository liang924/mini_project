import socket
import random
import time
import json

# === 基本設定 ===
client_ip = '192.168.92.1'
client_port = 5407
proxy_ip = '192.168.92.1'
proxy_port = 5406

loss_probability = 0.10   # 模擬丟包機率 10%
timeout_sec = 5           # 超過5秒沒收到封包則結束
N = 100000             # 總封包數（理論上應該收到）

# === 建立 UDP socket ===
c = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
c.bind((proxy_ip, proxy_port))
c.settimeout(timeout_sec)

print(
    f"[Proxy-Loss] Ready at {proxy_ip}:{proxy_port} | Loss={loss_probability*100:.1f}% | Expecting {N} packets")

# === 統計變數 ===
total_received = 0   # 實際收到的封包（含模擬丟棄）
total_lost = 0       # 模擬丟失的封包數量
forwarded_count = 0  # 實際轉發到 client 的封包數
unique_ids = set()   # 追蹤已見過的封包 id（避免重複計數）
start_time = time.time()

# === 主迴圈 ===
while True:
    try:
        recv_data, sender_addr = c.recvfrom(65535)
        total_received += 1

        try:
            msg = json.loads(recv_data.decode('utf-8'))
        except Exception:
            print(
                f"[Proxy-Loss] Warning: received non-JSON or invalid JSON from {sender_addr}: {recv_data!r}")
            continue

        # 支援不同可能的 id 欄位名稱
        raw_id = msg.get("id") if isinstance(msg, dict) else None
        if raw_id is None:
            raw_id = msg.get("seq") if isinstance(msg, dict) else None

        if raw_id is None:
            print(f"[Proxy-Loss] Warning: no 'id' field in message: {msg}")
            continue

        try:
            flag = int(raw_id)
        except Exception:
            print(f"[Proxy-Loss] Warning: invalid id value: {raw_id!r}")
            continue

        # 若已見過同一 id，仍視為收到但不再重複計入 unique_ids
        unique_ids.add(flag)

        # 模擬丟包
        if random.random() < loss_probability:
            total_lost += 1
            print(f"[Proxy-Loss] Packet {flag:06d} DROPPED")
        else:
            # 正常轉發給 client
            try:
                c.sendto(recv_data, (client_ip, client_port))
                forwarded_count += 1
            except Exception as e:
                print(f"[Proxy-Loss] Error sending packet {flag}: {e}")

        # 停止條件：已見到 N 個不同 id 或 forwarded_count/N 視需求調整
        if len(unique_ids) >= N:
            print(
                f"\n[Proxy-Loss] Seen {len(unique_ids)} unique packets (expected {N}), stopping.")
            break

    except socket.timeout:
        print("\n[Proxy-Loss] Timeout → no packets received for a while, stopping.")
        break
    except KeyboardInterrupt:
        print("\n[Proxy-Loss] Interrupted manually.")
        break
    except Exception as e:
        print(f"[Proxy-Loss] Error: {e}")
        break

# === 統計結果 ===
elapsed = time.time() - start_time
loss_rate = (total_lost * 100 / N) if N else 0.0

print("\n================ Statistics ================")
print(f"Total packets (N)     : {N}")
print(f"Loss rate                : {loss_rate:.2f}%")
print(f"Run time                 : {elapsed:.2f}s")
print("============================================")

c.close()
