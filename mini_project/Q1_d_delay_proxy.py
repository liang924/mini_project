import socket
import random
import time
import threading
import re

client_ip = '192.168.92.1'           
client_port = 5407
proxy_ip = '192.168.92.1'      
proxy_port = 5408                    

N = 100
delay_rate = 0.05
delay_time = 0.02  # 秒
count_delay = 0

c = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
c.bind((proxy_ip, proxy_port))

delayed_packets = set()
lock = threading.Lock()      # 控制封包集合
send_lock = threading.Lock() # 控制 socket 傳送

print(f"Proxy1 ({delay_rate*100:.0f}% delay) ready at {proxy_ip}:{proxy_port}")

def delay_func(data_recv, flag):
    time.sleep(delay_time)
    with send_lock:
        c.sendto(data_recv, (client_ip, client_port))
    with lock:
        if flag in delayed_packets:
            delayed_packets.remove(flag)
    print(f"---------- Packet {flag:3d} Released ----------")

while True:
    try:
        recv_data, client_address = c.recvfrom(65535)
        message = recv_data.decode('utf-8')

        # robustly extract the first integer (packet number) from the message
        m = re.search(r'\d+', message)
        if not m:
            print("Warning: couldn't parse packet number from:", message)
            continue
        flag = int(m.group())

        pick = random.random()

        with lock:
            if pick <= delay_rate and flag not in delayed_packets:
                delayed_packets.add(flag)
                count_delay += 1
                print(f"************ Packet {flag:3d} Delayed ************")
                t = threading.Thread(target=delay_func, args=(recv_data, flag))
                t.start()
            elif flag not in delayed_packets:
                with send_lock:
                    c.sendto(recv_data, (client_ip, client_port))

        if flag == N:
            break

    except KeyboardInterrupt:
        print("\n[Proxy stopped manually]")
        break
    except Exception as e:
        print("Error:", e)
        break

print("\n================ Statistics ================")
print(f"Total packets : {N}")
print(f"Delayed packets: {count_delay}")
print(f"Delay rate     = {count_delay * 100 / N:.2f}%")
print("============================================")

c.close()
