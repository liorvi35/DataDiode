import socket
import hashlib
import io
import sys
import os


FIRST_PROXY_ADDR = ("127.0.0.1", 5060)
NEW_FILE_NAME = "encrypt_sender"


def encrypt_file(file):
    md5_enc = hashlib.md5()
    chunk = file.read(io.DEFAULT_BUFFER_SIZE)
    while chunk:
        md5_enc.update(chunk)
        chunk = file.read(io.DEFAULT_BUFFER_SIZE)
    hex_rep = md5_enc.hexdigest()
    with open(NEW_FILE_NAME, "w") as file:
        file.write(hex_rep)


def send_file(sock, file):
    chunk = file.read(io.DEFAULT_BUFFER_SIZE)
    while chunk:
        sock.sendall(chunk)
        chunk = file.read(io.DEFAULT_BUFFER_SIZE)


def main():
    with open("file", "rb") as file:  # replace 'file' with 'sys.argv[1]'
        encrypt_file(file)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(FIRST_PROXY_ADDR)

    with open(NEW_FILE_NAME, "rb") as file:
        send_file(sock, file)
    os.remove(NEW_FILE_NAME)

    sock.shutdown(socket.SHUT_RDWR)
    sock.close()


if __name__ == "__main__":
    main()
