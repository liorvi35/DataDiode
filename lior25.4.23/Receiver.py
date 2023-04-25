import hashlib
import io
import socket
import sys
import tqdm
import time

TIMEOUT = 0.01
FAIL = 1
RECEIVER_ADDR = ("127.0.0.1", 12347)


def encrypt_file(file):
    try:
        md5 = hashlib.md5()
        data = file.read(io.DEFAULT_BUFFER_SIZE)
        while data:
            md5.update(data)
            data = file.read(io.DEFAULT_BUFFER_SIZE)
        file.seek(0)
        return md5.hexdigest()
    except (NameError, AttributeError, TypeError, IOError,
            OSError, FileNotFoundError, PermissionError) as e:
        print(f"[-] Error: {e}.")
        sys.exit(FAIL)


def recv_file(client_sock):
    with open(f"receiver", "wb") as file:
        with tqdm.tqdm(total=None, unit="B", unit_scale=True, desc="Receiving") as pb:
            data = client_sock.recv(io.DEFAULT_BUFFER_SIZE)
            while data:
                file.write(data)
                pb.update(len(data))
                time.sleep(TIMEOUT)
                data = client_sock.recv(io.DEFAULT_BUFFER_SIZE)



with socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP) as socket:
    socket.bind(RECEIVER_ADDR)
    socket.listen(300)

    while True:

        client, addr = socket.accept()

        recv_file(client)

        with open("receiver", "rb") as file:
            print(f"md5 = {file}")
