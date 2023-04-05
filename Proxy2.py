import socket
import io
import os


RECEIVER_ADDR = ("127.0.0.1", 5063)
SECOND_PROXY_ADDR = ("127.0.0.1", 5062)
NEW_FILE_NAME = "encrypt_proxy2"
START_MESSAGE = b"SOF"
END_MESSAGE = b"EOF"


def send_file(file):
    flow_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    flow_sock.connect(RECEIVER_ADDR)
    chunk = file.read(io.DEFAULT_BUFFER_SIZE)
    while chunk:
        flow_sock.sendall(chunk)
        chunk = file.read(io.DEFAULT_BUFFER_SIZE)
    flow_sock.shutdown(socket.SHUT_RDWR)
    flow_sock.close()


def recv_file(sock):
    with open(NEW_FILE_NAME, "wb") as file:
        chunk, client_addr = sock.recvfrom(io.DEFAULT_BUFFER_SIZE)
        while chunk != END_MESSAGE:
            file.write(chunk)
            chunk, client_addr = sock.recvfrom(io.DEFAULT_BUFFER_SIZE)


def main():
    try:
        server_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_sock.bind(SECOND_PROXY_ADDR)
        while True:
            client_msg, client_addr = server_sock.recvfrom(io.DEFAULT_BUFFER_SIZE)
            if client_msg == START_MESSAGE:
                recv_file(server_sock)
            with open(NEW_FILE_NAME, "rb") as file:
                send_file(file)
            os.remove(NEW_FILE_NAME)
    except KeyboardInterrupt:
        print("Closing Proxy2...")



if __name__ == "__main__":
    main()
