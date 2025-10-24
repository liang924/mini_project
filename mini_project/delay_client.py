import socket
import time

client_ip = '192.168.0.145'
client_port = 5405

c = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
c.bind((client_ip, client_port))
c.settimeout(10)

while True:
    try:
        data, addr = c.recvfrom(65535)
        recv_time = time.time()  # 接收時間
        msg = data.decode('utf-8')

        # 從封包訊息中取出 send_time
        # 格式：Packet 80 sended at t = 1761047115.85668
        parts = msg.split("t = ")
        send_time = float(parts[1]) if len(parts) > 1 else 0.0

        # 計算延遲
        delay = recv_time - send_time

        # 格式化顯示：對齊 + 清楚標示
        print(f"{msg:<45} | recv_time = {recv_time:.5f} | Packet delay = {delay:.5f} sec")

        # 若已收到最後一個封包
        if "Packet 100" in msg:
            print("**** All packets received. Stop client. ****")
            break

    except socket.timeout:
        print("**** Timeout while no input packet for 10 sec. ****")
        break
