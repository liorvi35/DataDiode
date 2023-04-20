import io
import socket
import time


SERVER_ADDR = ("127.0.0.1", 5060)
BUFFER_SIZE = io.DEFAULT_BUFFER_SIZE + 78
CONN_REQ = b"C"
ACK = b"A"
SEND_REQ = b"S"
WAITING = 0.1
END_OF_FILE = b"E"
TIMEOUT = 5


def send_acknowledgement(sock, client_addr, seq):
    if seq is None:
        sock.sendto(ACK, client_addr)
    else:
        sock.sendto(f"{ACK.decode()}:{seq}".encode(), client_addr)
    time.sleep(WAITING)


def main():

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as sock:

        sock.bind(SERVER_ADDR)

        while True:

            data, client_addr = sock.recvfrom(BUFFER_SIZE)

            if data == CONN_REQ:

                send_acknowledgement(sock, client_addr, None)

                print(f"{client_addr} is connected.")

                data, client_addr = sock.recvfrom(BUFFER_SIZE)

                if data == SEND_REQ:
                    send_acknowledgement(sock, client_addr, None)

                    with open("recv", "wb") as file:

                        data, client_addr = sock.recvfrom(BUFFER_SIZE)

                        while data[0:1] != b"F":
                            file.write(data[data.index(b":") + 1:])

                            file.flush()

                            send_acknowledgement(sock, client_addr, int(data.split(b":")[0][1:]))

                            data, client_addr = sock.recvfrom(BUFFER_SIZE)

                        send_acknowledgement(sock, client_addr, None)

                        print("file received.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nYoad Tamar is my king :)")
