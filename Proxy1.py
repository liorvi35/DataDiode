"""
Network Diode
Assignment 1 of `Protection of Communications Protocols` course at Ariel-University

this file contains the implementation of the `Proxy1` which is the
second entity in the architecture's data-flow (2/4)
the Proxy1 is the part who receives the file from the Sender using
TCP communication and sends it to Proxy2 using (Reliable-)UDP communication.

:version: 1.6
:since: 26/04/2023
:authors: Lior Vinman & Yoad Tamar
"""

import socket
import tqdm
import sys
import os
import io

SECOND_PROXY_ADDR = ("10.9.0.4", 60573)  # address of proxy2
FIRST_PROXY_ADDR = ("10.9.0.3", 61328)  # address of proxy1
BUFFER_SIZE = io.DEFAULT_BUFFER_SIZE  # buffer size for send/receive
TEMP_FILE_NAME = "p1"  # temporary file name, saved as: p1_addr
SEND_REQ = b"N1:1:S"  # request to send
TIMEOUT = 1  # packet receive timeout
SUCCESS = 0  # ok
ACK = b"A"  # RUDP's acknowledgment signal
FAIL = 1  # !ok
SPLITTER = b":"  # payload info splitter
EMPTY_MESSAGE = b""  # empty data
MAX_CONNECTIONS = 300  # maximal TCP clients


def build_payload(final, seq, data):
    """
    this function builds the RUDP packet's payload
    :param final: True if this is final segment, else false
    :param seq: segment's relative sequence number
    :param data: the segment itself
    :return: encoded string in format: <N/F><Seq>:<length(Data)>:<Data>
    """
    ch = "F" if final else "N"
    return f"{ch}{seq}:{len(data)}:{data.decode()}".encode()


def check_recv(sock, packet):
    """
    this file checks if RUDP packet has been received or not
    :param sock: object of UDP socket to send data via
    :param packet: packet to send
    :return: (True,msg) if packet has been sent (data is what received), else (False,None)
    """
    sock.settimeout(TIMEOUT)
    while True:
        try:
            msg, address = sock.recvfrom(BUFFER_SIZE)
            sock.settimeout(None)
            return True, msg
        except (socket.timeout, socket.error):
            sock.sendto(packet, SECOND_PROXY_ADDR)
            continue
    sock.settimeout(None)
    return False, None


def send_file(addr):
    """
    this function sends RUDP packets
    :param addr: client address to send to
    """
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as flow_sock:
        flow_sock.sendto(SEND_REQ, SECOND_PROXY_ADDR)
        status, data = check_recv(flow_sock, SEND_REQ)
        if not status:
            sys.exit(FAIL)
        with open(f"{TEMP_FILE_NAME}_{addr}", "rb") as file:
            with tqdm.tqdm(total=os.path.getsize(f"{TEMP_FILE_NAME}_{addr}"),
                           unit="B", unit_scale=True, desc="Sending") as pb:
                seq = 2
                data = file.read(BUFFER_SIZE)
                while data:
                    flow_sock.sendto(build_payload(False, seq, data), SECOND_PROXY_ADDR)
                    status, to_send = check_recv(flow_sock, build_payload(False, seq, data))
                    if not status:
                        sys.exit(FAIL)
                    if int(to_send.split(SPLITTER)[1].decode()) != seq:
                        ack = int(to_send.split(SPLITTER)[1].decode())
                        file.seek(0)
                        file.read(ack)
                        seq = ack + 1
                        data = file.read(BUFFER_SIZE)
                        continue
                    pb.update(len(data))
                    data = file.read(BUFFER_SIZE)
                    seq += 1
                flow_sock.sendto(build_payload(True, seq, EMPTY_MESSAGE), SECOND_PROXY_ADDR)
                status, data = check_recv(flow_sock, build_payload(True, seq, EMPTY_MESSAGE))
                if data != ACK:
                    sys.exit(FAIL)


def main():
    """
    main function, it creates a TCP socket which receives the file from the Sender
    then in opens a (R)UDP socket that sends the file to seconds proxy
    :return:
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP) as main_sock:
            main_sock.bind(FIRST_PROXY_ADDR)
            main_sock.listen(MAX_CONNECTIONS)
            print("Listening for incoming connections...\n")

            while True:
                client_sock, client_addr = main_sock.accept()
                print(f"Accepted connection from: '{client_addr}'.")
                with open(f"{TEMP_FILE_NAME}_{client_addr}", "wb") as file:
                    with tqdm.tqdm(total=None, unit="B", unit_scale=True, desc="Receiving") as pb:
                        data = client_sock.recv(BUFFER_SIZE)
                        while data:
                            file.write(data)
                            pb.update(len(data))
                            data = client_sock.recv(BUFFER_SIZE)
                    print("File has been received.")
                client_sock.close()

                send_file(client_addr)
                print("File has been sent.\n")

                os.remove(f"{TEMP_FILE_NAME}_{client_addr}")
    except KeyboardInterrupt:
        print("\nClosing proxy1.")
        sys.exit(SUCCESS)
    except (Exception, socket.error) as e:
        print(f"Error: {e}.")
        sys.exit(FAIL)


if __name__ == "__main__":
    main()
