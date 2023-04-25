import io
import socket

BUFFER_SIZE = io.DEFAULT_BUFFER_SIZE


with socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP) as sock:

    sock.connect(("127.0.0.1", 10203))

    with open("file", "rb") as file:
        data = file.read(BUFFER_SIZE)
        while data:
            sock.sendall(data)
            data = file.read(BUFFER_SIZE)

    sock.shutdown(socket.SHUT_RDWR)