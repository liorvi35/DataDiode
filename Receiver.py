import socket
import io
import os

RECEIVER_ADDR = ("127.0.0.1", 5063)
NEW_FILE_NAME = "encrypted_file"
MAXIMUM_CONNECTIONS = 50


def recv_file(sock):
    with open(NEW_FILE_NAME, "wb") as file:
        chunk = sock.recv(io.DEFAULT_BUFFER_SIZE)
        while chunk:
            file.write(chunk)
            chunk = sock.recv(io.DEFAULT_BUFFER_SIZE)


def main():
    try:
        server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_sock.bind(RECEIVER_ADDR)
        server_sock.listen(MAXIMUM_CONNECTIONS)
        while True:
            client_sock, client_addr = server_sock.accept()
            recv_file(client_sock)
    except KeyboardInterrupt:
        print("Closing Receiver...")
    finally:
        if not server_sock.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR):
            server_sock.close()


if __name__ == "__main__":
    main()
