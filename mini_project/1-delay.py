import socket
import random
import time
import threading
import json

client_ip = '192.168.92.1'
client_port = 5407
proxy_ip = '192.168.92.1'
proxy_port = 5408

N = 100000
delay_probability = 0.05
delay_duration = 0.02
count_delay = 0
total_packets = 0
running = True

c = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
c.bind((proxy_ip, proxy_port))
c.settimeout(1.0)  # ⭐ 保證不會永遠卡在 recvfrom()

delayed_packets = set()
lock = threading.Lock()
send_lock = threading.Lock()
threads = []

print(f"[Proxy-Delay] Ready at {proxy_ip}:{proxy_port} | Delay={delay_probability*100:.1f}%, Duration={delay_duration*1000:.0f}ms")

def delay_func(data_recv, flag):
    time.sleep(delay_duration)
    with send_lock:
        if running:  # 確保程式還沒結束才送
            c.sendto(data_recv, (client_ip, client_port))
    with lock:
        delayed_packets.discard(flag)
    print(f"[Proxy-Delay] Released packet {flag:05d}")

start_time = time.time()

try:
    while running:
        try:
            recv_data, client_address = c.recvfrom(65535)
            total_packets += 1
            msg = json.loads(recv_data.decode('utf-8'))
            flag = msg.get("id", -1)
        except socket.timeout:
            continue  # 繼續 loop，讓 Ctrl+C 有機會觸發
        except Exception:
            continue

        pick = random.random()
        with lock:
            if pick <= delay_probability and flag not in delayed_packets:
                delayed_packets.add(flag)
                count_delay += 1
                print(f"[Proxy-Delay] Delaying packet {flag:05d}")
                t = threading.Thread(target=delay_func, args=(recv_data, flag))
                t.start()
                threads.append(t)
            elif flag not in delayed_packets:
                with send_lock:
                    c.sendto(recv_data, (client_ip, client_port))

except KeyboardInterrupt:
    print("\n[Proxy-Delay] Interrupted manually, finishing pending packets...")
    running = False
finally:
    for t in threads:
        t.join(timeout=1)

    elapsed = time.time() - start_time
    delay_rate = count_delay * 100 / max(1, total_packets)
    print("\n================ Statistics ================")
    print(f"Total packets      : {total_packets}")
    print(f"Delayed packets    : {count_delay}")
    print(f"Delay rate         : {delay_rate:.2f}%")
    print(f"Run time           : {elapsed:.2f}s")
    print("============================================")

    c.close()
