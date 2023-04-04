import socket

RECVEIVER_ADDR = ('127.0.0.1', 61950)
NUM_CONN = 200


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(RECVEIVER_ADDR)
    sock.listen(NUM_CONN)
    while True:
        csock, caddr = sock.accept()
        with open(f"receiver.txt", "wb") as file:
            chunk = csock.recv(1024)
            while chunk:
                file.write(chunk)
                chunk = csock.recv(1024)


if __name__ == '__main__':
    main()