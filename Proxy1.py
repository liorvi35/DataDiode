import socket
import os
import io


FIRST_PROXY_ADDR = ("127.0.0.1", 5060)
DATA_DIODE_ADDR = ("127.0.0.1", 5061)
MAXIMUM_CONNECTIONS = 50
NEW_FILE_NAME = "encrypt_proxy1"
START_MESSAGE = b"SOF"
END_MESSAGE = b"EOF"


def send_file(file):
    flow_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    flow_sock.sendto(START_MESSAGE, DATA_DIODE_ADDR)
    chunk = file.read(io.DEFAULT_BUFFER_SIZE)
    while chunk:
        flow_sock.sendto(chunk, DATA_DIODE_ADDR)
        chunk = file.read(io.DEFAULT_BUFFER_SIZE)
    flow_sock.sendto(END_MESSAGE, DATA_DIODE_ADDR)
    flow_sock.close()


def recv_file(sock):
    with open(NEW_FILE_NAME, "wb") as file:
        chunk = sock.recv(io.DEFAULT_BUFFER_SIZE)
        while chunk:
            file.write(chunk)
            chunk = sock.recv(io.DEFAULT_BUFFER_SIZE)


def main():
    try:
        server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_sock.bind(FIRST_PROXY_ADDR)
        server_sock.listen(MAXIMUM_CONNECTIONS)

        while True:
            client_sock, client_addr = server_sock.accept()
            recv_file(client_sock)

            with open(NEW_FILE_NAME, "rb") as file:
                send_file(file)
            os.remove(NEW_FILE_NAME)

            client_sock.close()
    except KeyboardInterrupt:
        print("Closing Proxy1...")
    finally:
        if not server_sock.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR):
            server_sock.close()


if __name__ == "__main__":
    main()
