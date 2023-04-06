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

RECEIVER_ADDR = ("127.0.0.1", 5063)  # address of receiver
NEW_FILE_NAME = "encrypted_file"  # name for creation of a temporary file
MAXIMUM_CONNECTIONS = 50  # maximal number of connections via TCP


def recv_file(sock):
    """
    this function receives file in segments through a TCP socket
    :param sock: file descriptor of a TCP socket
    """
    try:
        with open(NEW_FILE_NAME, "wb") as file:
            chunk = sock.recv(io.DEFAULT_BUFFER_SIZE)
            while chunk:
                file.write(chunk)
                chunk = sock.recv(io.DEFAULT_BUFFER_SIZE)   # receiving file with TCP (step 'd-2')
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
                print("[+] File has been received.\n------------------------------")

    except KeyboardInterrupt:
        print("[-] Closing Receiver...")
    except socket.error | IOError as e:
        print(f"[-] Error: {e}.")
        sys.exit(1)
    finally:
        if main_sock:
            main_sock.close()


if __name__ == "__main__":
    main()
    sys.exit(0)
