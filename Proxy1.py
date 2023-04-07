"""
this file is implementation for the proxy 1, second entity in data flow (2/5)
proxy 1 is the part who receiving the encrypted message (file) via TCP (Transmission Control Protocol) socket
and sending to the data-diode server using a UDP (User Datagram Protocol) socket.

it should be noted here that TCP is not a "unidirectional" protocol because, firstly, it requires
an establishment of a connection-session, what causes a "3-Way-Handshake" process that sends 3 packets
in both way ("SYN": client -> server, "SYN-ACK": server -> client, "ACK": client -> server"). moreover, after
each receiving is sends an acknowledgment ("ACK") for receiving, what also makes the data flow both ways,
because of that - to save a "unidirectional" data flow, a UDP is used (which is not establishing a session,
and is not sending acknowledgments) to send the data for out diode.

:version: 1.3
:since: 06.04.2023
:authors: Lior Vinman & Yoad Tamar
"""

import socket
import os
import io
import sys
import time
import tqdm

FIRST_PROXY_ADDR = ("127.0.0.1", 5060)  # address of first proxy server
DATA_DIODE_ADDR = ("127.0.0.1", 5061)  # address of data-diode server
MAXIMUM_CONNECTIONS = 50  # maximal number of connections via TCP
NEW_FILE_NAME = "encrypt_proxy1"  # name for creation of a temporary file
START_MESSAGE = b"S"  # message that points on a starting of sending file segments - "Start"
END_MESSAGE = b"E"  # message that points on an ending of sending file segments - "End"
CHUNK_SIZE = 1  # chunk size of receiving and sending file
TIMEOUT = 0.1  # timeout after each sending or receiving segment


def send_file(file):
    """
    this function creates a UDP socket and sends file (in segments) through it
    :param file: file descriptor of a file that should be sent
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as flow_sock:  # creating a UDP ("flow") socket
            with tqdm.tqdm(total=(8 * os.path.getsize(NEW_FILE_NAME)), unit="b", unit_scale=True, desc="Sending") as pb:
                flow_sock.sendto(START_MESSAGE, DATA_DIODE_ADDR)  # sending start message
                chunk = file.read(CHUNK_SIZE)
                while chunk:
                    flow_sock.sendto(chunk, DATA_DIODE_ADDR)  # sending file in chunks (step 'c-1')
                    pb.update(len(8 * chunk))
                    time.sleep(TIMEOUT)
                    chunk = file.read(CHUNK_SIZE)
                flow_sock.sendto(END_MESSAGE, DATA_DIODE_ADDR)  # sending stop message
    except socket.error as e:
        print(f"[-] Error occurred while sending file: {e}.")
        sys.exit(1)


def recv_file(sock):
    """
    this function receives in segments the file via TCP socket
    :param sock: file descriptor of a TCP socket that file should be received from
    """
    try:
        with open(NEW_FILE_NAME, "wb") as file:  # creating temporary file
            with tqdm.tqdm(total=(8 * os.path.getsize(NEW_FILE_NAME)), unit="b", unit_scale=True, desc="Receiving") as pb:
                chunk = sock.recv(CHUNK_SIZE)  # receiving file in segments
                while chunk:
                    file.write(chunk)
                    pb.update(len(8 * chunk))
                    time.sleep(TIMEOUT)
                    chunk = sock.recv(CHUNK_SIZE)
    except OSError as e:
        print(f"[-] Error occurred while receiving file: {e}.")
        sys.exit(1)


def main():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as main_sock:
            main_sock.bind(FIRST_PROXY_ADDR)
            main_sock.listen(MAXIMUM_CONNECTIONS)
            print("[+] Listening for incoming connections...")

            while True:
                client_sock, client_addr = main_sock.accept()
                print(f"[+] Accepted connection from 'proxy2'.")

                recv_file(client_sock)
                print("[+] File has been received.")

                with open(NEW_FILE_NAME, "rb") as file:
                    send_file(file)
                os.remove(NEW_FILE_NAME)
                print("[+] File has been sent.\n------------------------------")

    except KeyboardInterrupt:
        print("\n[-] Closing Proxy 1...")
    except socket.error | IOError as e:
        print(f"[-] Error: {e}.")
        sys.exit(1)
    finally:
        if main_sock:
            main_sock.close()


if __name__ == "__main__":
    main()
    sys.exit(0)
