import io
import socket
import time


SERVER_ADDR = ("127.0.0.1", 5060)
BUFFER_SIZE = io.DEFAULT_BUFFER_SIZE + 96
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


def check_recv(sock, packet):
    print("in check recv")
    timeout = 0
    sock.settimeout(TIMEOUT)
    while timeout != 3:
        try:
            msg, address = sock.recvfrom(BUFFER_SIZE)
            print("SUCC")
            sock.settimeout(None)
            return True, msg
        except (socket.timeout, socket.error):
            timeout += 1
            print(f"TIME OUT... THIS IS {timeout}/{3} retransmission")
            sock.sendto(packet, SERVER_ADDR)
            time.sleep(WAITING)
            continue
    sock.settimeout(None)
    print("FAIL")
    return False, None


def main():

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as sock:

        sock.bind(SERVER_ADDR)

        while True:

            data, client_addr = sock.recvfrom(BUFFER_SIZE)

            if data == CONN_REQ:

                send_acknowledgement(sock, client_addr, None)

                print(f"{client_addr} is connected.")

                # data, client_addr = sock.recvfrom(BUFFER_SIZE)

                status, data = check_recv(sock, send_acknowledgement(sock, client_addr, None))

                if not status:
                    continue

                if data == SEND_REQ:
                    # send_acknowledgement(sock, client_addr, None)

                    with open("recv", "wb") as file:

                        data, client_addr = sock.recvfrom(BUFFER_SIZE)

                        last_seq = -1

                        while data[0:1] != b"F":

                            print(int(data.split(b":")[1]))

                            if int(data.split(b":")[1]) != len(data[(data.find(b":", data.find(b":") + 1)) + 1:]):

                                print("INCORRECT CHUNK SIZE")

                                if last_seq == -1:
                                    send_acknowledgement(sock, client_addr, 0)

                                else:
                                    send_acknowledgement(sock, client_addr, last_seq)

                                    last_seq = (int(data.split(b":")[0][1:]) + 1)

                                continue

                            elif int(data.split(b":")[0][1:]) != (last_seq + 1):

                                print("DUP or OOO", (last_seq+1), " split=", int(data.split(b":")[0][1:]))

                                if last_seq == -1:
                                    send_acknowledgement(sock, client_addr, 0)

                                else:
                                    send_acknowledgement(sock, client_addr, last_seq)

                                    last_seq = (int(data.split(b":")[0][1:]) + 1)

                                continue

                            last_seq += 1
                            print("ls=", last_seq)

                            file.write(data[(data.find(b":", data.find(b":") + 1)) + 1:])

                            send_acknowledgement(sock, client_addr, int(data.split(b":")[0][1:]))

                            # data, client_addr = sock.recvfrom(BUFFER_SIZE)

                            status, data = check_recv(sock, send_acknowledgement(sock, client_addr, int(data.split(b":")[0][1:])))

                            if not status:
                                continue

                        send_acknowledgement(sock, client_addr, None)

                        print("file received.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nYoad Tamar is my king :)")
