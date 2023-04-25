import io
import os
import socket
import sys
import time
import tqdm

FIRST_PROXY_ADDR = ("127.0.0.1", 12345)
SECOND_PROXY_ADDR = ("127.0.0.1", 12346)
MAX_CONN = 300
TEMP_FILE_NAME = "tmp_p1"
TIMEOUT = 0.01

SEND_REQ = b"N1:1:S"
BUFFER_SIZE = io.DEFAULT_BUFFER_SIZE
ACK = b"A"


def build_payload(final, seq, data):
    ch = "F" if final else "N"
    return f"{ch}{seq}:{len(data)}:{data.decode()}".encode()


def check_recv(sock, packet):
    sock.settimeout(TIMEOUT)
    while True:
        try:
            msg, address = sock.recvfrom(io.DEFAULT_BUFFER_SIZE)
            sock.settimeout(None)
            return True, msg
        except (socket.timeout, socket.error):
            sock.sendto(packet, SECOND_PROXY_ADDR)
            time.sleep(TIMEOUT)
            continue
    sock.settimeout(None)
    return False, None


def recv_file(client_sock, client_addr):
    with open(f"{TEMP_FILE_NAME}_{client_addr}", "wb") as file:
        with tqdm.tqdm(total=None, unit="B", unit_scale=True, desc="Receiving") as pb:
            data = client_sock.recv(io.DEFAULT_BUFFER_SIZE)
            while data:
                file.write(data)
                pb.update(len(data))
                time.sleep(TIMEOUT)
                data = client_sock.recv(io.DEFAULT_BUFFER_SIZE)


def send_file(client_addr):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as sock:
        sock.sendto(SEND_REQ, SECOND_PROXY_ADDR)
        status, data = check_recv(sock, SEND_REQ)
        if not status:
            sys.exit(1)
        with open(f"{TEMP_FILE_NAME}_{client_addr}", "rb") as file:
            with tqdm.tqdm(total=os.path.getsize(f"{TEMP_FILE_NAME}_{client_addr}"),
                           unit="B", unit_scale=True, desc="Sending") as pb:
                seq = 2
                data = file.read(BUFFER_SIZE)
                while data:
                    sock.sendto(build_payload(False, seq, data), SECOND_PROXY_ADDR)
                    time.sleep(TIMEOUT)
                    status, to_send = check_recv(sock, build_payload(False, seq, data))
                    if not status:
                        sys.exit(1)
                    if int(to_send.split(b":")[1].decode()) != seq:
                        ack = int(to_send.split(b":")[1].decode())
                        file.seek(0)
                        file.read(ack * 1)
                        seq = ack + 1
                        data = file.read(BUFFER_SIZE)
                        continue
                    ack = int(to_send.split(b":")[1].decode())
                    pb.update(len(data))
                    data = file.read(BUFFER_SIZE)
                    seq += 1
                sock.sendto(build_payload(True, seq, b""), SECOND_PROXY_ADDR)
                time.sleep(TIMEOUT)
                status, data = check_recv(sock, build_payload(True, seq, b""))
                if data != ACK:
                    sys.exit(1)


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP) as main_sock:
        main_sock.bind(FIRST_PROXY_ADDR)
        main_sock.listen(MAX_CONN)
        print("[+] Waiting for connections...")

        while True:
            client_sock, client_addr = main_sock.accept()
            print(f"[+] Accepted connection from: '{client_addr}'.")

            recv_file(client_sock, client_addr)
            print(f"[+] File has been received.")

            send_file(client_addr)
            print(f"[+] File has been sent.")

            client_sock.close()


if __name__ == "__main__":
    main()
