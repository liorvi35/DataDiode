import socket
import io
import sys
import time

# Format of data-packet: <N/F><Number>:<Size>:<Data>
# Format of ACK-packet: A:<Number>

SERVER_ADDR = ("127.0.0.1", 5060)
BUFFER_SIZE = io.DEFAULT_BUFFER_SIZE
CONN_REQ = b"C"
ACK = b"A"
WAITING = 0.1
MSG = b"Hello World"
SEND_REQ = b"S"
END_OF_FILE = b"E"
FILE_NAME = "file"
TIMEOUT = 5

DUP = 1
OUT_OF_ORDER = 2


def build_payload(final, seq, data):
    ch = "F" if final else "N"
    return f"{ch}{seq}:{len(data)}:{data.decode()}".encode()


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

        sock.sendto(CONN_REQ, SERVER_ADDR)
        time.sleep(WAITING)

        status, data = check_recv(sock, CONN_REQ)

        print("status=", status, " data=", data)

        if not status:
            sys.exit(1)

        if data != ACK:
            sys.exit(1)

        print("Connected")

        sock.sendto(SEND_REQ, SERVER_ADDR)
        time.sleep(WAITING)

        status, data = check_recv(sock, SEND_REQ)

        if not status:
            sys.exit(1)

        if data != ACK:
            sys.exit(1)

        with open(FILE_NAME, "rb") as file:

            seq = timeout = expected_seq = 0

            data = file.read(BUFFER_SIZE)

            while data:

                sock.sendto(build_payload(False, seq, data), SERVER_ADDR)

                time.sleep(WAITING)

                status, data = check_recv(sock, build_payload(False, seq, data))

                if not status:
                    sys.exit(1)

                if int(data.split(b":")[1].decode()) != expected_seq:

                    file.seek(0)
                    file.read(int(data.split(b":")[1].decode()) * BUFFER_SIZE)

                    seq = int(data.split(b":")[1].decode()) + 1

                    expected_seq = seq

                    data = file.read(BUFFER_SIZE)

                    continue

                data = file.read(BUFFER_SIZE)

                seq += 1
                expected_seq += 1

            sock.sendto(build_payload(True, seq, b""), SERVER_ADDR)

            time.sleep(WAITING)

            status, data = check_recv(sock, build_payload(True, seq, b""))

            if not status:
                sys.exit(1)

            if data != ACK:
                sys.exit(1)

            print("file transferred.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nYoad Tamar is my king :)")
