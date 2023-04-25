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
SEND_REQ = b"N1:1:S"
END_OF_FILE = b"E"
FILE_NAME = "p1"
TIMEOUT = 5


def build_payload(final, seq, data):
    ch = "F" if final else "N"
    return f"{ch}{seq}:{len(data)}:{data.decode()}".encode()


def check_recv(sock, packet):
    print("in check recv")
    timeout = 0
    sock.settimeout(TIMEOUT)
    while timeout != 100:
        try:
            msg, address = sock.recvfrom(BUFFER_SIZE)
            print("SUCC")
            sock.settimeout(None)
            return True, msg
        except (socket.timeout, socket.error):
            timeout += 1
            print(f"TIME OUT... THIS IS {timeout}/{10} retransmission")
            sock.sendto(packet, SERVER_ADDR)
            time.sleep(WAITING)
            continue
    sock.settimeout(None)
    print("FAIL")
    return False, None

def send_file():

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as sock:

        sock.sendto(SEND_REQ, SERVER_ADDR)

        status, data = check_recv(sock, SEND_REQ)
        # data, address = sock.recvfrom(BUFFER_SIZE)

        if not status:
            sys.exit(1)

        print("begin transfer file...")

        with open("p1", "rb") as file:

            seq = 2
            timeout = 0

            data = file.read(BUFFER_SIZE)

            while data:

                print(f"seq send: {seq}")
                sock.sendto(build_payload(False, seq, data), SERVER_ADDR)

                time.sleep(WAITING)

                status, data = check_recv(sock, build_payload(False, seq, data))
                #data, address = sock.recvfrom(BUFFER_SIZE)

                if not status:
                    sys.exit(1)

                if int(data.split(b":")[1].decode()) != seq:

                    ack = int(data.split(b":")[1].decode())
                    print(f"wrong seq! \nack recv: {ack}")

                    file.seek(0)
                    file.read(ack * 1)

                    seq = ack + 1

                    data = file.read(BUFFER_SIZE)

                    continue

                ack = int(data.split(b":")[1].decode())
                print(f"ack recv: {ack}")
                data = file.read(BUFFER_SIZE)
                seq += 1

            sock.sendto(build_payload(True, seq, b""), SERVER_ADDR)

            time.sleep(WAITING)

            status, data = check_recv(sock, build_payload(True, seq, b""))
            #data, address = sock.recvfrom(BUFFER_SIZE)

            # if not status:
            #     sys.exit(1)

            if data != ACK:
                sys.exit(1)

            print("file transferred.")
            
            
            
            
def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP) as sock:

        sock.bind(("127.0.0.1", 10203))

        sock.listen(300)

        while True:
            client, addr = sock.accept()

            with open("p1", "wb") as file:
                data = client.recv(io.DEFAULT_BUFFER_SIZE)
                while data:
                    file.write(data)
                    data = client.recv(io.DEFAULT_BUFFER_SIZE)

            send_file()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nYoad Tamar is my king :)")

