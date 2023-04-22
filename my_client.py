import socket
import time
import io

SERVER_ADDRESS = ("127.0.0.1", 5060)
BUFFER_SIZE = io.DEFAULT_BUFFER_SIZE

SPLITTER = b":"
ACK = b"A"
CONN_REQ = b"C"
SEND_REQ = b"S"
FINAL_PACKET = b"F"
NOT_FINAL_PACKET = b"N"

TIMEOUT = 3


def make_segmentation():
    segments_list = []
    with open("file", "rb") as file:
        segment = file.read(BUFFER_SIZE)
        while segment:
            segments_list.append(segment)
            segment = file.read(BUFFER_SIZE)
    return segments_list


data_list = make_segmentation()

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as sock:

    for i, j in enumerate(data_list):
        ch = NOT_FINAL_PACKET.decode()

        if i == len(data_list) - 1:
            ch = FINAL_PACKET.decode()

        sock.sendto(f"{ch}:{i}:{j.decode()}".encode(), SERVER_ADDRESS)

        ack_received = False
        while not ack_received:
            try:
                sock.settimeout(TIMEOUT)
                ack, addr = sock.recvfrom(BUFFER_SIZE)

                if ack == ACK:
                    ack_received = True

            except socket.timeout:
                sock.sendto(f"{ch}:{i}:{j.decode()}".encode(), SERVER_ADDRESS)




