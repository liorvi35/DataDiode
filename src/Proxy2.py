"""
Network Diode
Assignment 1 of `Protection of Communications Protocols` course at Ariel-University

this file contains the implementation of the `Proxy2` which is the
third entity in the architecture's data-flow (3/4)
the Proxy2 is the part who receives the file from the Proxy1 using
RUDP communication and sends it to the Receiver using TCP communication.

:version: 1.6
:since: 26/04/2023
:authors: Lior Vinman & Yoad Tamar
"""

import socket
import tqdm
import sys
import io
import os

SECOND_PROXY_ADDR = ("10.9.0.4", 60573)  # address of proxy2
FIRST_PROXY_ADDR = ("10.9.0.3", 61328)  # address of proxy1
RECEIVER_ADDR = ("10.9.0.5", 56875)  # address of receiver
BUFFER_SIZE = (2 * io.DEFAULT_BUFFER_SIZE) + (2 * sys.getsizeof(b":")) + (2 * sys.getsizeof(int)) \
              + max(sys.getsizeof(b"A"), sys.getsizeof(b"N"), sys.getsizeof(b"F"))  # buffer size for send/receive
TEMP_FILE_NAME = "p2"  # temporary file name, saved as: p2_addr
ACK = b"A"  # RUDP's acknowledgment signal
SEND_REQ = b"N1:1:S"  # request to send
TIMEOUT = 1
LAST_PACKET = b"F"  # last packet identifier
SPLITTER = b":"  # payload info splitter
FAIL = 1  # !ok
SUCCESS = 0  # ok


def send_acknowledgement(sock, client_addr, seq):
    """
    this function sends an ack signal about received segments
    :param sock: object of (R)UDP socket
    :param client_addr: client address to send to
    :param seq: None if should be sent a "common" signal, or a last segment sequence number
    """
    if seq is None:
        sock.sendto(ACK, client_addr)
    else:
        sock.sendto(f"{ACK.decode()}:{seq}".encode(), client_addr)


def send_file(addr):
    """
    this function opens a TCP socket and sends through it a file
    :param addr: client's address
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP) as sock:
            sock.connect(RECEIVER_ADDR)
            with open(f"{TEMP_FILE_NAME}_{addr}", "rb") as file:
                with tqdm.tqdm(total=os.path.getsize(f"{TEMP_FILE_NAME}_{addr}"),
                               unit="B", unit_scale=True, desc="Sending") as pb:
                    data = file.read(BUFFER_SIZE)
                    while data:
                        sock.sendall(data)
                        pb.update(len(data))
                        data = file.read(BUFFER_SIZE)
            sock.shutdown(socket.SHUT_RDWR)
        print("File has been sent.\n")
    except (Exception, socket.error) as e:
        print("Error: {e}.")
        sys.exit(FAIL)


def main():
    """
    main function, opens a (R)UDP socket and receiving the file,
    then opens a TCP socket and sends the file to receiver
    """
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as sock:
        sock.bind(SECOND_PROXY_ADDR)
        print("Listening for incoming connections...\n")
        while True:
            data, client_addr = sock.recvfrom(BUFFER_SIZE)
            if data[0:1] == LAST_PACKET:
                send_acknowledgement(sock, client_addr, None)
                continue
            if data != SEND_REQ:
                continue
            send_acknowledgement(sock, client_addr, 1)
            print(f"Accepted connection from: '{client_addr}'.")
            data, client_addr = sock.recvfrom(BUFFER_SIZE)
            if int(data[1:2]) != 2:
                continue
            with open(f"{TEMP_FILE_NAME}_{client_addr}", "wb") as file:
                with tqdm.tqdm(total=None, unit="B", unit_scale=True, desc="Receiving") as pb:
                    seq = 1
                    expected_seq = 2
                    while data[0:1] != LAST_PACKET:
                        if int(data.split(SPLITTER)[1]) != len(data[(data.find(SPLITTER, data.find(SPLITTER) + 1)) + 1:]):
                            send_acknowledgement(sock, client_addr, seq)
                            data, client_addr = sock.recvfrom(BUFFER_SIZE)
                            continue
                        elif int(data.split(SPLITTER)[0][1:]) != expected_seq:
                            send_acknowledgement(sock, client_addr, seq)
                            data, client_addr = sock.recvfrom(BUFFER_SIZE)
                            continue
                        seq = expected_seq
                        expected_seq += 1
                        pb.update(len(data[(data.find(SPLITTER, data.find(SPLITTER) + 1)) + 1:]))
                        file.write(data[(data.find(SPLITTER, data.find(SPLITTER) + 1)) + 1:])
                        send_acknowledgement(sock, client_addr, seq)
                        data, client_addr = sock.recvfrom(BUFFER_SIZE)
                    send_acknowledgement(sock, client_addr, None)
            print("File has been received.")
            send_file(client_addr)
            os.remove(f"{TEMP_FILE_NAME}_{client_addr}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nClosing proxy2...")
    except (Exception, socket.error) as e:
        print(f"Error: {e}.")
        sys.exit(FAIL)
    sys.exit(SUCCESS)
