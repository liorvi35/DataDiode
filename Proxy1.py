"""
1) bind on (x,y) = ("127.0.0.1", 6090)
2) recv enripter file from sender
"""
import math
import socket

PROXY1_ADDR = ("127.0.0.1", 61947)
DIODE_ADDR = ("127.0.0.1", 61948)
NUM_CONN = 200


def send_diode(file):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    chunk = file.read(1024)
    while chunk:
        sock.sendto(chunk, DIODE_ADDR)
        chunk = file.read(1024)
    sock.close()


def main():
    server_sock_fd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock_fd.bind(PROXY1_ADDR)
    server_sock_fd.listen(NUM_CONN)
    while True:
        client_sock_fd, client_address = server_sock_fd.accept()
        with open(f"secret.txt_{client_address}", "wb") as file:
            chunk = client_sock_fd.recv(1024)
            while chunk:
                file.write(chunk)
                chunk = client_sock_fd.recv(1024)
        with open(f"secret.txt_{client_address}", "rb") as file:
            send_diode(file)
        client_sock_fd.close()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("closing proxy1...")


