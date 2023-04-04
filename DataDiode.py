"""
1) recv from proxy1 udp

2) send proxy2 udp
"""
import socket

DIODE_ADDR = ("127.0.0.1", 61948)
PROXY2_ADDR = ("127.0.0.1", 61949)


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
