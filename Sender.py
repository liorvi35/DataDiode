"""
1) file -> md5-hash

2) open conn with proxy1

3) send file to proxy1 via TCP
"""
import hashlib
import socket

CURR_FILE = "file"
NEW_FILE_NAME = "secret_ket.txt"
PROXY1_ADDR = ("127.0.0.1", 61947)
CHUNK_SIZE = 1024


def encrypt_md5(file):
    md5_enc = hashlib.md5()
    chunk = file.read(CHUNK_SIZE)
    while chunk:
        md5_enc.update(chunk)
        chunk = file.read(CHUNK_SIZE)
    hexadecimal_rep = md5_enc.hexdigest()
    with open(NEW_FILE_NAME, "w") as output:
        output.write(hexadecimal_rep)


def send_file(sock_fd, file):
    chunk = file.read(CHUNK_SIZE)
    while chunk:
        sock_fd.sendall(chunk)
        chunk = file.read(CHUNK_SIZE)


def main():
    with open(CURR_FILE, "rb") as file:
        encrypt_md5(file)

    sock_fd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock_fd.connect(PROXY1_ADDR)

    with open(NEW_FILE_NAME, "rb") as file:
        send_file(sock_fd, file)

    sock_fd.shutdown(socket.SHUT_RDWR)
    sock_fd.close()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("closing sender...")
