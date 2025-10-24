import socket
import time
import json
import numpy as np

client_ip = '192.168.92.1'
client_port = 5407

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind((client_ip, client_port))
s.settimeout(0.5)  # 每次等待資料的 timeout

received = set()
delays = []  # 儲存每個封包延遲（ms）
per_path_count = {}
N = 100000

print(f"[CLIENT] Listening on {client_ip}:{client_port} ...")

start_time = time.time()
last_recv_time = start_time
end_grace = 2.0  # 若超過此秒數沒有新封包且已收到至少一個則結束

while True:
    try:
        data, _ = s.recvfrom(65535)
        recv_time = time.time()
        last_recv_time = recv_time

        try:
            msg = json.loads(data.decode('utf-8'))
        except Exception:
            print(f"[CLIENT] Warning: invalid JSON received: {data!r}")
            continue

        # 安全取得 seq/id、path、timestamp
        raw_seq = msg.get("id") if isinstance(msg, dict) else None
        if raw_seq is None:
            raw_seq = msg.get("seq") if isinstance(msg, dict) else None

        try:
            seq = int(raw_seq)
        except Exception:
            print(f"[CLIENT] Warning: invalid seq/id: {raw_seq!r}")
            continue

        path = msg.get("path", "?")
        send_t = msg.get("timestamp", None)

        # 統計 per-path
        per_path_count[path] = per_path_count.get(path, 0) + 1

        if send_t is not None:
            try:
                send_t = float(send_t)
                delay_ms = (recv_time - send_t) * 1000.0
                delays.append(delay_ms)
            except Exception:
                delay_ms = None
        else:
            delay_ms = None

        received.add(seq)

        # 即時輸出
        print(
            f"Packet {seq:06d} sent via Path{path} at t = {send_t} | recv_time={recv_time:.6f} | delay={delay_ms:.2f} ms")

        # 若已收到預期數量則可以結束
        if len(received) >= N:
            print("[CLIENT] Received all expected packets.")
            break

    except socket.timeout:
        # 若超過 end_grace 秒沒有新封包且已收到至少一個，則結束
        if (time.time() - last_recv_time) > end_grace and len(received) > 0:
            print("[CLIENT] No new packets for a while — stopping.")
            break
        else:
            continue
    except KeyboardInterrupt:
        print("[CLIENT] Interrupted by user.")
        break
    except Exception as e:
        print(f"[CLIENT] Error: {e}")
        break

end_time = time.time()
total_time = end_time - start_time
received_count = len(received)

# 使用 numpy 計算統計（有 numpy 才用）
if delays:
    avg_delay = float(np.mean(delays))
else:
    avg_delay = med_delay = std_delay = 0.0

loss_count = max(0, N - received_count)
loss_rate = (loss_count * 100.0 / N) if N else 0.0

# 統計輸出
print("\n================ Statistics ================")
print(f"Total Packets Sent:      {N}")
print(f"Packets Received:        {received_count}")
print(f"Packets Lost (est):      {loss_count} ({loss_rate:.2f}%)")
print(f"Average Delay:           {avg_delay:.2f} ms")
print(f"Total Transmission Time: {total_time:.2f} s")
print("============================================")
