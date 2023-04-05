import socket
import io
import os

SECOND_PROXY_ADDR = ("127.0.0.1", 5062)
DATA_DIODE_ADDR = ("127.0.0.1", 5061)
NEW_FILE_NAME = "encrypt_data_diode"
START_MESSAGE = b"SOF"
END_MESSAGE = b"EOF"


def recv_file(sock):
    with open(NEW_FILE_NAME, "wb") as file:
        chunk, client_addr = sock.recvfrom(io.DEFAULT_BUFFER_SIZE)
        while chunk != END_MESSAGE:
            file.write(chunk)
            chunk, client_addr = sock.recvfrom(io.DEFAULT_BUFFER_SIZE)


def send_file(sock, file):
    sock.sendto(START_MESSAGE, SECOND_PROXY_ADDR)
    chunk = file.read(io.DEFAULT_BUFFER_SIZE)
    while chunk:
        sock.sendto(chunk, SECOND_PROXY_ADDR)
        chunk = file.read(io.DEFAULT_BUFFER_SIZE)
    sock.sendto(END_MESSAGE, SECOND_PROXY_ADDR)


def main():
    try:
        server_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_sock.bind(DATA_DIODE_ADDR)
        while True:
            client_msg, client_addr = server_sock.recvfrom(io.DEFAULT_BUFFER_SIZE)
            if client_msg == START_MESSAGE:
                recv_file(server_sock)
            with open(NEW_FILE_NAME, "rb") as file:
                send_file(server_sock, file)
            os.remove(NEW_FILE_NAME)
    except KeyboardInterrupt:
        print("Closing Data-Diode...")


if __name__ == "__main__":
    main()
