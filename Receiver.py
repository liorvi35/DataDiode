"""
this file is implementation for the proxy 2, fifth entity in data flow (5/5)
receiver is the final part of this architecture who finally receiving
the encrypted message (file) via TCP (Transmission Control Protocol) socket.

this part is the end-point of our system, and here we can be sure that the data
flew only in one direction, as our diode is ensuring.

:version: 1.3
:since: 06.04.2023
:authors: Lior Vinman & Yoad Tamar
"""

import socket
import io
import sys
import tqdm
import time
import os

RECEIVER_ADDR = ("127.0.0.1", 5063)  # address of receiver
NEW_FILE_NAME = "encrypted_file"  # name for creation of a temporary file
MAXIMUM_CONNECTIONS = 50  # maximal number of connections via TCP
CHUNK_SIZE = 1  # chunk size of receiving and sending file
TIMEOUT = 0.1  # timeout after each sending or receiving segment


def recv_file(sock):
    """
    this function receives file in segments through a TCP socket
    :param sock: file descriptor of a TCP socket
    """
    try:
        with open(NEW_FILE_NAME, "wb") as file:
            with tqdm.tqdm(total=(8 * os.path.getsize(NEW_FILE_NAME)), unit="b", unit_scale=True, desc="Receiving") as pb:
                chunk = sock.recv(CHUNK_SIZE)
                while chunk:
                    file.write(chunk)
                    pb.update(len(8 * chunk))
                    time.sleep(TIMEOUT)
                    chunk = sock.recv(1)   # receiving file with TCP (step 'd-2')
    except socket.error as e:
        print(f"[-] Error occurred while receiving file: {e}.")
        sys.exit(1)


def main():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as main_sock:
            main_sock.bind(RECEIVER_ADDR)
            main_sock.listen(MAXIMUM_CONNECTIONS)
            print("[+] Listening for incoming connections...")

            while True:
                client_sock, client_addr = main_sock.accept()
                print(f"[+] Accepted connection from: {client_addr}.")

                recv_file(client_sock)

                with open(NEW_FILE_NAME, "r") as file:
                    ciphertext = file.read(io.DEFAULT_BUFFER_SIZE)

                print(f"[+] File has been received. Ciphertext is: '{ciphertext}'.\n------------------------------")

    except KeyboardInterrupt:
        print("\n[-] Closing Receiver...")
    except socket.error | IOError as e:
        print(f"[-] Error: {e}.")
        sys.exit(1)
    finally:
        if main_sock:
            main_sock.close()


if __name__ == "__main__":
    main()
    sys.exit(0)
