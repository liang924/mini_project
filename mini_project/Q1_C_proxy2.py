import socket
import random
import time

client_ip = '192.168.4.248'           
client_port = 5407
proxy_ip = '192.168.4.251'      
proxy_port = 5408                   

c = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
c.bind((proxy_ip, proxy_port))

print("Proxy1 ready")

while True:
    try:
        data, addr = c.recvfrom(65535)
        msg = data.decode('utf-8')
        print("Forwarding:", msg)

        # 轉發給 UDP Client
        c.sendto(data, (client_ip, client_port))

        if msg.strip().startswith("Packet 100 "):  
            print("All packets forwarded, stop proxy.")
            break


    except Exception as e:
        print("Error:", e)
        break