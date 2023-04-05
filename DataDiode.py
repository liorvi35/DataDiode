"""

"""

import os
import socket

DATA_DIODE_ADDR = ("127.0.0.1", 61948) # IPv4 address and port of the data-diode
PROXY2_ADDR = ("127.0.0.1", 61947) # IPv4 address and port of proxy2


def recv_proxy1(sock):
    with open("recv_diode", "wb") as file:
        chunk, addr = sock.recvfrom(1024)
        while chunk:
            file.write(chunk)
            chunk, addr = sock.recvfrom(1024)


def send_proxy2():
    pass


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(DIODE_ADDR)
    while True:
        recv_proxy1(sock)
        send_proxy2(sock)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("closing diode...")
