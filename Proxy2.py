"""
this file is implementation for the proxy 2, fourth entity in data flow (4/5)
proxy 2 is the part who receiving the encrypted message (file) via UDP (User Datagram Protocol) socket
and sending to the receiver using a TCP (Transmission Control Protocol) socket.

here is the point that we are after the "iron wall", we got inside the system and from now can use
two-directional protocols, which means we can use TCP to ensure reliability.

:version: 1.3
:since: 06.04.2023
:authors: Lior Vinman & Yoad Tamar
"""

import socket
import io
import os
import sys
import tqdm
import time

RECEIVER_ADDR = ("127.0.0.1", 5063)  # address of receiver
SECOND_PROXY_ADDR = ("127.0.0.1", 5062)  # address of proxy 2 server
NEW_FILE_NAME = "encrypt_proxy2"  # name for creation of a temporary file
START_MESSAGE = b"S"  # message that points on a starting of sending file segments - "Start Of File"
END_MESSAGE = b"E"  # message that points on an ending of sending file segments - "End Of File"
CHUNK_SIZE = 1  # chunk size of receiving and sending file
TIMEOUT = 0.1  # timeout after each sending or receiving segment


def send_file(file):
    """
    this function sends a file via TCP socket
    :param file: file descriptor of a file that should be sent
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as flow_sock:
            flow_sock.connect(RECEIVER_ADDR)  # connecting to receiver
            with tqdm.tqdm(total=(8 * os.path.getsize(NEW_FILE_NAME)), unit="b", unit_scale=True, desc="Sending") as pb:
                chunk = file.read(CHUNK_SIZE)
                while chunk:
                    flow_sock.sendall(chunk)  # sending file to receiver with TCP (step 'd-1')
                    pb.update(len(8 * chunk))
                    time.sleep(TIMEOUT)
                    chunk = file.read(CHUNK_SIZE)
                flow_sock.shutdown(socket.SHUT_RDWR)
    except socket.error as e:
        print(f"[-] Error occurred while sending file: {e}.")
        sys.exit(1)


def recv_file(sock):
    """
    this function receives file in segments through given UDP socket
    :param sock: file descriptor for UDP socket that should receive the file
    """
    try:
        with open(NEW_FILE_NAME, "wb") as file:
            with tqdm.tqdm(total=(8 * os.path.getsize(NEW_FILE_NAME)), unit="b", unit_scale=True, desc="Receiving") as pb:
                chunk, client_addr = sock.recvfrom(io.DEFAULT_BUFFER_SIZE)
                while chunk != END_MESSAGE:
                    file.write(chunk)
                    pb.update(len(8 * chunk))
                    chunk, client_addr = sock.recvfrom(io.DEFAULT_BUFFER_SIZE)  # receiving the file
    except socket.error as e:
        print(f"[-] Error occurred while receiving file: {e}.")
        sys.exit(1)


def main():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as main_sock:
            main_sock.bind(SECOND_PROXY_ADDR)
            print("[+] Server bound and waiting for input...")

            while True:
                client_msg, client_addr = main_sock.recvfrom(io.DEFAULT_BUFFER_SIZE)
                if client_msg == START_MESSAGE:
                    recv_file(main_sock)
                print("[+] File has been received.")

                with open(NEW_FILE_NAME, "rb") as file:
                    send_file(file)
                os.remove(NEW_FILE_NAME)
                print("[+] File has been sent.\n------------------------------")

    except KeyboardInterrupt:
        print("\nClosing Proxy2...")
    except socket.error | IOError as e:
        print(f"[-] Error: {e}.")
        sys.exit(1)
    finally:
        if main_sock:
            main_sock.close()


if __name__ == "__main__":
    main()
    sys.exit(0)
