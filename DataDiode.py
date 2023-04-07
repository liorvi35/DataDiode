"""
this file is implementation for the data diode, third entity in data flow (3/5)
data diode is the part who receiving the encrypted message (file) via UDP (User Datagram Protocol) socket
and sending to proxy 2 server using a UDP socket.

since data diode fully based on UDP sockets, it ensures that data will flow only in one direction,
that: [sender <-> proxy1] -> [data-diode] -> [proxy2 <-> receiver], we can think about the data-diode
like as on an "iron wall" which data can only reach inside but do not can get outside

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

SECOND_PROXY_ADDR = ("127.0.0.1", 5062)  # address of second proxy server
DATA_DIODE_ADDR = ("127.0.0.1", 5061)  # address of data-diode server
NEW_FILE_NAME = "encrypt_data_diode"  # name for creation of a temporary file
START_MESSAGE = b"S"  # message that points on a starting of sending file segments - "Start"
END_MESSAGE = b"E"  # message that points on an ending of sending file segments - "End"
CHUNK_SIZE = 1  # chunk size of receiving and sending file
TIMEOUT = 0.1  # timeout after each sending or receiving segment


def recv_file(sock):
    """
    this function receives a file in segments from a UDP socket
    :param sock: file descriptor of UDP socket
    """
    try:
        with open(NEW_FILE_NAME, "wb") as file:
            with tqdm.tqdm(total=(8 * os.path.getsize(NEW_FILE_NAME)), unit="b", unit_scale=True, desc="Receiving") as pb:
                chunk, client_addr = sock.recvfrom(CHUNK_SIZE)
                while chunk != END_MESSAGE:  # receiving the file
                    file.write(chunk)
                    pb.update(len(8 * chunk))
                    time.sleep(TIMEOUT)
                    chunk, client_addr = sock.recvfrom(CHUNK_SIZE)
    except socket.error as e:
        print(f"[-] Error occurred while receiving file: {e}.")
        sys.exit(1)


def send_file(sock, file):
    """
    this function is sending file in segments via a UDP socket
    :param sock: file descriptor of UDP socket to send the file through it
    :param file: file descriptor of a file to send
    """
    try:
        sock.sendto(START_MESSAGE, SECOND_PROXY_ADDR)  # sending start message that indicates of file sending
        with tqdm.tqdm(total=(8 * os.path.getsize(NEW_FILE_NAME)), unit="b", unit_scale=True, desc="Sending") as pb:
            chunk = file.read(CHUNK_SIZE)
            while chunk:
                sock.sendto(chunk, SECOND_PROXY_ADDR)  # sending file in chunks (step 'c-2')
                pb.update(len(8 * chunk))
                time.sleep(TIMEOUT)
                chunk = file.read(CHUNK_SIZE)
        sock.sendto(END_MESSAGE, SECOND_PROXY_ADDR)  # sending start message that indicates of ending of file sending
    except socket.error as e:
        print(f"[-] Error occurred while sending file: {e}.")
        sys.exit(1)


def main():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as main_sock:
            main_sock.bind(DATA_DIODE_ADDR)
            print("[+] Server bound and waiting for input...")

            while True:
                client_msg, client_addr = main_sock.recvfrom(io.DEFAULT_BUFFER_SIZE)
                if client_msg == START_MESSAGE:
                    recv_file(main_sock)
                print("[+] File has been received.")

                with open(NEW_FILE_NAME, "rb") as file:
                    send_file(main_sock, file)
                os.remove(NEW_FILE_NAME)
                print("[+] File has been sent.\n------------------------------")

    except KeyboardInterrupt:
        print("\n[-] Closing Data-Diode...")
    except socket.error | IOError as e:
        print(f"[-] Error: {e}.")
        sys.exit(1)
    finally:
        if main_sock:
            main_sock.close()


if __name__ == "__main__":
    main()
