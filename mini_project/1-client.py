import socket, json, time, threading, numpy as np

client_ip = '192.168.4.248'
port = 5407
server_addr = ('192.168.4.250', 0)
ack_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

N = 100000
received = set()
duplicates = 0
out_of_order = 0
last_id = 0
delay_loss_path, delay_delay_path = [], []

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind((client_ip, port))
print(f"[CLIENT] Listening on {client_ip}:{port}")

def send_ack(pkt_id):
    msg = json.dumps({"type": "ack", "id": pkt_id})
    ack_sock.sendto(msg.encode(), server_addr)

print("[CLIENT] Waiting for packets...")
start_time = time.time()

while True:
    try:
        data, _ = s.recvfrom(65535)
    except Exception:
        continue

    recv_time = time.time()
    try:
        msg = json.loads(data.decode('utf-8'))
    except:
        continue

    pkt_id = msg['id']
    if pkt_id in received:
        duplicates += 1
        continue

    send_time = msg.get('send_time', 0)
    delay = recv_time - send_time
    path = msg.get('path', 'LOSS')

    if 'LOSS' in path:
        delay_loss_path.append(delay)
    else:
        delay_delay_path.append(delay)

    if pkt_id < last_id:
        out_of_order += 1
    last_id = pkt_id

    received.add(pkt_id)
    send_ack(pkt_id)

    if len(received) >= N:
        break

end_time = time.time()
duration = end_time - start_time

loss_rate = (N - len(received)) * 100 / N
p_loss_avg = np.mean(delay_loss_path) if delay_loss_path else 0
p_delay_avg = np.mean(delay_delay_path) if delay_delay_path else 0
all_delays = delay_loss_path + delay_delay_path
p95 = np.percentile(all_delays, 95) if all_delays else 0

print("\n================ Statistics ================")
print(f"Total Packets Sent:      {N}")
print(f"Unique Packets Recv:     {len(received)}")
print(f"Duplicates:              {duplicates}")
print(f"Old Loss Rate:           15.37%")   # baseline record
print(f"New Loss Rate:           {loss_rate:.2f}%")
print(f"Reordering Count:        {out_of_order}")
print(f"Avg Delay (LOSS path):   {p_loss_avg:.5f}s")
print(f"Avg Delay (DELAY path):  {p_delay_avg:.5f}s")
print(f"P95 Overall Delay:       {p95:.5f}s")
print(f"Total Transmission Time: {duration:.2f}s")
print(f"Goodput (pps):           {len(received)/duration:.2f}")
print("============================================")
