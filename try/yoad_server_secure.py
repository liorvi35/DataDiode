import io
import socket
import time

SERVER_ADDR = ("127.0.0.1", 5060)
BUFFER_SIZE = io.DEFAULT_BUFFER_SIZE + 96
CONN_REQ = b"C"
ACK = b"A"
SEND_REQ = b"N1:1:S"
WAITING = 0.1
END_OF_FILE = b"E"
TIMEOUT = 5


def send_acknowledgement(sock, client_addr, seq):
    if seq is None:
        sock.sendto(ACK, client_addr)
    else:
        sock.sendto(f"{ACK.decode()}:{seq}".encode(), client_addr)
    time.sleep(WAITING)


def build_acknowledgement(seq):
    if seq is None:
        return ACK
    else:
        return f"{ACK.decode()}:{seq}".encode()


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

            print("waiting...")

            data, client_addr = sock.recvfrom(BUFFER_SIZE)

            if data[0:1] == b"F":
                send_acknowledgement(sock, client_addr, None)
                continue

            if data != SEND_REQ:
                print("not secured!!!!!!!!")
                continue

            send_acknowledgement(sock, client_addr, 1)

            data, client_addr = sock.recvfrom(BUFFER_SIZE)

            if int(data[1:2]) != 2:
                #print(data)
                print("not secured")
                continue

            with open("recv", "wb") as file:

                seq = 1
                expected_seq = 2

                while data[0:1] != b"F":

                    # Packet: N123:len:data

                    if int(data.split(b":")[1]) != len(data[(data.find(b":", data.find(b":") + 1)) + 1:]):

                        print("INCORRECT CHUNK SIZE")
                        expected = int(data.split(b":")[1])
                        data_len = len(data[(data.find(b":", data.find(b":") + 1)) + 1:])
                        print(f"expected: {expected} get: {data_len}")

                        send_acknowledgement(sock, client_addr, seq)

                        # status, data = check_recv(sock, build_acknowledgement(seq))
                        # if not status:
                        #     break

                        data, client_addr = sock.recvfrom(BUFFER_SIZE)

                        continue

                    elif int(data.split(b":")[0][1:]) != expected_seq:

                        print("Wrong seq!")
                        print("seq recv: ", int(data.split(b":")[0][1:]), " expected seq:", expected_seq)

                        send_acknowledgement(sock, client_addr, seq)
                        print(f"send last seq recv: {seq}")

                        data, client_addr = sock.recvfrom(BUFFER_SIZE)

                        # status, data = check_recv(sock, build_acknowledgement(seq))
                        # if not status:
                        #     break

                        continue

                    print("correct packet, seq: ", int(data.split(b":")[0][1:]))

                    # print("seq recv: ", int(data.split(b":")[0][1:]), " expected seq:", expected_seq)

                    seq = expected_seq
                    expected_seq += 1

                    file.write(data[(data.find(b":", data.find(b":") + 1)) + 1:])

                    # send_acknowledgement(sock, client_addr, int(data.split(b":")[0][1:]))
                    send_acknowledgement(sock, client_addr, seq)
                    print(f"send seq: {seq}")

                    data, client_addr = sock.recvfrom(BUFFER_SIZE)

                    # status, data = check_recv(sock, build_acknowledgement(seq))
                    #
                    # if not status:
                    #     break

                send_acknowledgement(sock, client_addr, None)

                print("file received.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nYoad Tamar is my king :)")
