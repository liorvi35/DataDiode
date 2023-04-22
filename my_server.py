import io
import socket
import time
import sys
import io

SERVER_ADDRESS = ("127.0.0.1", 5060)
BASE_SIZE = io.DEFAULT_BUFFER_SIZE
BUFFER_SIZE = BASE_SIZE + sys.getsizeof(b":") + max(sys.getsizeof(b"N"), sys.getsizeof(b"F"))

data_segments = {}

SPLITTER = b":"
ACK = b"A"
CONN_REQ = b"C"
SEND_REQ = b"S"
FINAL_PACKET = b"F"
NOT_FINAL_PACKET = b"N"

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as sock:

    sock.bind(SERVER_ADDRESS)

    while True:

        data = SPLITTER

        while data.split(SPLITTER)[0] != FINAL_PACKET:

            data, addr = sock.recvfrom(BUFFER_SIZE)

            print("data=", data.decode())

            if int(data.split(SPLITTER)[1].decode()) not in data_segments.keys():
                data_segments[int(data.split(SPLITTER)[1].decode())] = data.split(SPLITTER)[2]

            sock.sendto(SPLITTER, addr)

        print("file received")

        print("list=", data_segments)
        print("len=", len(data_segments))

        with open("recv", "wb") as file:
            for i in data_segments.values():
                file.write(i)
            data_segments.clear()

        break



