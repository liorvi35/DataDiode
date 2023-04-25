"""
Network Diode
Assignment 1 of `Protection of Communications Protocols` course at Ariel-University

this file contains the implementation of the `Reciver` which is the
fourth entity in the architecture's data-flow (4/4)
the Receiver is the part who (finally) receives the file from the Sender using TCP communication.

:version: 1.6
:since: 26/04/2023
:authors: Lior Vinman & Yoad Tamar
"""

import io
import socket
import tqdm
import hashlib
import sys

FAIL = 1  # !ok
SUCCESS = 0  # ok
MAX_CONNECTIONS = 300  # maximal TCP clients
RECEIVER_ADDR = ("10.9.0.5", 56875)  # address of receiver
FILE_NAME = "recv"  # name for received file, saved as: recv_addr


def hash_file(file):
    """
    this function hashes a file into MD5
    same function that Sender has
    :param file: object of file
    :return: hexadecimal representation of the hash
    """
    try:
        md5 = hashlib.md5()
        data = file.read(io.DEFAULT_BUFFER_SIZE)
        while data:
            md5.update(data)
            data = file.read(io.DEFAULT_BUFFER_SIZE)
        file.seek(0)
        return md5.hexdigest()
    except Exception as e:
        print(f"Error: {e}.")
        sys.exit(FAIL)


def main():
    """
    main function, it opens a TCP socket and receives the file from Proxy2
    then hashes the file into MD5
    :return:
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP) as sock:
        sock.bind(RECEIVER_ADDR)
        sock.listen(MAX_CONNECTIONS)
        print("Listening for incoming connections...\n")
        while True:
            client_sock, client_addr = sock.accept()
            print(f"Accepted connection from: '{client_addr}'.")

            with open(f"{FILE_NAME}_{client_addr}", "wb") as file:
                with tqdm.tqdm(total=None, unit="B", unit_scale=True, desc="Receiving") as pb:
                    data = client_sock.recv(io.DEFAULT_BUFFER_SIZE)
                    while data:
                        file.write(data)
                        pb.update(len(data))
                        data = client_sock.recv(io.DEFAULT_BUFFER_SIZE)

                client_sock.close()

            with open(f"{FILE_NAME}_{client_addr}", "rb") as file:
                print(f"File has been received.\nMD5 = '{hash_file(file)}'.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nClosing proxy2...")
    except (Exception, socket.error) as e:
        print(f"Error: {e}.")
        sys.exit(FAIL)
    sys.exit(SUCCESS)
