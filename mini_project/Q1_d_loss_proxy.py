import socket
import random
import time

client_ip = '192.168.92.1'           
client_port = 5407
proxy_ip = '192.168.92.1'      
proxy_port = 5406                    

count_loss = 0
count_recv = 0
N = 100
timeout_sec = 5  # 超過5秒沒收到封包就結束

c = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
c.bind((proxy_ip, proxy_port))
c.settimeout(timeout_sec)  # 設定接收逾時

print(f"Proxy1 (10% loss) ready at {proxy_ip}:{proxy_port}")

start_time = time.time()

while True:
    try:
        recv_data, client_address = c.recvfrom(65535)
        message_from_send = recv_data.decode('utf-8')
        temp = message_from_send.split()
        flag = int(temp[1])
        count_recv += 1

        # 以 10% 機率丟包
        if random.random() <= 0.1:
            print(f"************ Packet {flag:3d} Loss ************")
            count_loss += 1
        else:
            c.sendto(recv_data, (client_ip, client_port))

        # 若收到足夠封包就提早結束
        if count_recv >= N:
            break

    except socket.timeout:
        print(f"\nNo packets received for {timeout_sec} seconds → Ending session.")
        break

    except KeyboardInterrupt:
        print("\n[Proxy stopped manually]")
        break

    except Exception as e:
        print("Error:", e)
        break

# 結束後顯示掉包率
loss_rate = count_loss * 100 / max(1, count_recv)
print(f"\nTotal packets processed: {count_recv}")
print(f"Lost packets: {count_loss}")
print(f"Loss rate = {loss_rate:.2f}%")

c.close()
