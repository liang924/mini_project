import socket
import time

proxy_ip = '192.168.4.251'
proxy_port = 5406

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

for i in range(1, 101):
    message = "Packet "+str(format(i,'3d'))+" sended at t = " + str(format(time.time(),'.5f'))
    print(message)

    s.sendto(message.encode('utf-8'), (proxy_ip, proxy_port))

    time.sleep(0.01)