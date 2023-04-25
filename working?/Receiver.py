import io
import socket

with socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP) as sock:

    sock.bind(("127.0.0.1", 12345))

    sock.listen(300)

    while True:
        client, addr = sock.accept()

        with open("recv", "wb") as file:
            data = client.recv(io.DEFAULT_BUFFER_SIZE)
            while data:
                file.write(data)
                data = client.recv(io.DEFAULT_BUFFER_SIZE)
