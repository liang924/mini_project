import socket
import time

client_ip = '192.168.4.248'
client_port = 5407

c = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
c.bind((client_ip, client_port))
c.settimeout(10)

while True:
    try:
        data, addr = c.recvfrom(65535)
        recv_time = time.time()  # 接收時間（秒）
        msg = data.decode('utf-8')

        # 從 message 中取出 send_time
        # 原始格式：Packet 80 sended at t = 1761047115.85668
        parts = msg.split("t = ")
        send_time = float(parts[1]) if len(parts) > 1 else 0.0

        # 計算延遲
        delay = recv_time - send_time

        # 顯示三個重點時間資訊
        print(f"{msg} | recv_time = {recv_time:.5f} | delay = {delay:.5f} sec")

        if "Packet 100" in msg:
            print("All packets received. Stop client.")
            break

    except socket.timeout:
        print("**** Timeout: no packets received in 10 sec ****")
        break

