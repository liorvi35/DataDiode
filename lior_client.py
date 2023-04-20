import socket
import io
import sys
import time
import os

# Format of data-packet: <N/F><Number>:<Data>
# Format of ACK-packet: A:<Number>

SERVER_ADDR = ("127.0.0.1", 5060)
BUFFER_SIZE = io.DEFAULT_BUFFER_SIZE
CONN_REQ = b"C"
ACK = b"A"
WAITING = 0.1
MSG = b"Hello World"
SEND_REQ = b"S"
END_OF_FILE = b"E"
FILE_NAME = "file"

DUP = 1
OUT_OF_ORDER = 2


def build_payload(final, seq, data):
    ch = "F" if final else "N"
    return f"{ch}{seq}:{data.decode()}".encode()


def main():

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as sock:

        sock.sendto(CONN_REQ, SERVER_ADDR)
        time.sleep(WAITING)

        data, server_addr = sock.recvfrom(BUFFER_SIZE)

        if data != ACK:
            sys.exit(1)

        print("Connected")

        sock.sendto(SEND_REQ, SERVER_ADDR)
        time.sleep(WAITING)

        data, server_addr = sock.recvfrom(BUFFER_SIZE)

        if data != ACK:
            sys.exit(1)

        with open(FILE_NAME, "rb") as file:

            seq = timeout = expected_seq = 0

            data = file.read(BUFFER_SIZE)

            while data:

                sock.sendto(build_payload(False, seq, data), SERVER_ADDR)

                time.sleep(WAITING)

                data, server_addr = sock.recvfrom(BUFFER_SIZE)

                if int(data.split(b":")[1].decode()) != expected_seq:
                    sys.exit(1)

                data = file.read(BUFFER_SIZE)

                seq += 1
                expected_seq += 1

            sock.sendto(build_payload(True, seq, b""), SERVER_ADDR)

            time.sleep(WAITING)

            data, server_addr = sock.recvfrom(BUFFER_SIZE)

            if data != ACK:
                sys.exit(1)

            print("file transferred.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nYoad Tamar is my king :)")
