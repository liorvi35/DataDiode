
import socket

PROXY2_ADDR = ("127.0.0.1", 61949)
RECVEIVER_ADDR = ('127.0.0.1', 61950)



def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(PROXY2_ADDR)

    with open("recv_proxy2", "wb") as file:
        chunk, addr = sock.recvfrom(1024)
        while chunk:
            file.write(chunk)
            chunk, addr = sock.recvfrom(1024)
    sock.close()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(RECVEIVER_ADDR)
    chunk = file.read(1024)
    while chunk:
        sock.sendall(chunk)
        chunk = file.read(1024)
    sock.close()

if __name__ == '__main__':
    main()

