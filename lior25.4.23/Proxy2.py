import io
import sys
import time
import socket
import os
import tqdm

BUFFER_SIZE = io.DEFAULT_BUFFER_SIZE + 2 * sys.getsizeof(b":")\
              + max(sys.getsizeof(b"N"), sys.getsizeof(b"F")) + 2 * sys.getsizeof(int)

FIRST_PROXY_ADDR = ("127.0.0.1", 12345)
SECOND_PROXY_ADDR = ("127.0.0.1", 12346)
RECEIVER_ADDR = ("127.0.0.1", 12347)
MAX_CONN = 300
TEMP_FILE_NAME = "tmp_p2"
TIMEOUT = 0.01

SEND_REQ = b"N1:1:S"
ACK = b"A"
FINAL_PACKET = b"F"


def send_file():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP) as sock:
        sock.connect(RECEIVER_ADDR)

        with open("file", "rb") as file:
            with tqdm.tqdm(total=os.path.getsize("file"), unit="B", unit_scale=True, desc="Sending") as pb:
                data = file.read(io.DEFAULT_BUFFER_SIZE)
                while data:
                    sock.sendall(data)
                    pb.update(len(data))
                    time.sleep(TIMEOUT)
                    data = file.read(io.DEFAULT_BUFFER_SIZE)
        print(f"[+] File has been sent.")



def send_acknowledgement(sock, client_addr, seq):
    if seq is None:
        sock.sendto(ACK, client_addr)
    else:
        sock.sendto(f"{ACK.decode()}:{seq}".encode(), client_addr)
    time.sleep(TIMEOUT)


def recv_file():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as sock:
        sock.bind(SECOND_PROXY_ADDR)
        while True:
            data, client_addr = sock.recvfrom(BUFFER_SIZE)
            if data[0:1] == FINAL_PACKET:
                send_acknowledgement(sock, client_addr, None)
                continue
            if data != SEND_REQ:
                continue
            send_acknowledgement(sock, client_addr, 1)
            data, client_addr = sock.recvfrom(BUFFER_SIZE)
            if int(data[1:2]) != 2:
                continue
            with open(TEMP_FILE_NAME, "wb") as file:
                with tqdm.tqdm(total=None, unit="B", unit_scale=True, desc="Receiving") as pb:
                    seq = 1
                    expected_seq = 2
                    while data[0:1] != b"F":
                        if int(data.split(b":")[1]) != len(data[(data.find(b":", data.find(b":") + 1)) + 1:]):
                            expected = int(data.split(b":")[1])
                            data_len = len(data[(data.find(b":", data.find(b":") + 1)) + 1:])
                            send_acknowledgement(sock, client_addr, seq)
                            data, client_addr = sock.recvfrom(BUFFER_SIZE)
                            continue
                        elif int(data.split(b":")[0][1:]) != expected_seq:
                            send_acknowledgement(sock, client_addr, seq)
                            data, client_addr = sock.recvfrom(BUFFER_SIZE)
                            continue
                        seq = expected_seq
                        expected_seq += 1
                        pb.update(len(data[(data.find(b":", data.find(b":") + 1)) + 1:]))
                        file.write(data[(data.find(b":", data.find(b":") + 1)) + 1:])
                        send_acknowledgement(sock, client_addr, seq)
                        data, client_addr = sock.recvfrom(BUFFER_SIZE)
                    send_acknowledgement(sock, client_addr, None)



def main():



if __name__ == '__main__':
    main()
