"""
Network Diode
Assignment 1 of `Protection of Communications Protocols` course at Ariel-University

this file contains the implementation of the `Sender` which is the
first entity in the architecture's data-flow (1/4)
the Sender is the part who choose a file and sends it to first
proxy server via a TCP communication.

:version: 1.6
:since: 26/04/2023
:authors: Lior Vinman & Yoad Tamar
"""

import hashlib
import socket
import tqdm
import sys
import io
import os

FIRST_PROXY_ADDR = ("10.9.0.3", 61328)  # address of proxy1
BUFFER_SIZE = io.DEFAULT_BUFFER_SIZE  # buffer size for send/receive
SUCCESS = 0  # ok
FAIL = 1  # !ok


def hash_file(file):
    """
    this function hashes a file into MD5
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
    main function, firstly it opens the file and hashes into MD5,
    then opens a connection with first proxy server and sends him the file
    """
    if len(sys.argv) != 2:
        print("Usage: 'python3 Sender.py <file>'.")
        sys.exit(FAIL)

    with open(sys.argv[1], "rb") as file:
        print(f"MD5 = '{hash_file(file)}'.")

        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP) as main_sock:
                main_sock.connect(FIRST_PROXY_ADDR)
                print(f"Established connection with: '{FIRST_PROXY_ADDR}'.")

                with tqdm.tqdm(total=os.path.getsize(sys.argv[1]), unit="B", unit_scale=True, desc="Sending") as pb:
                    data = file.read(BUFFER_SIZE)
                    while data:
                        main_sock.sendall(data)
                        pb.update(len(data))
                        data = file.read(BUFFER_SIZE)
                print("File has been sent.")
                main_sock.shutdown(socket.SHUT_RDWR)
        except KeyboardInterrupt:
            print("\nClosing sender.")
        except (Exception, socket.error) as e:
            print(f"Error: {e}.")
            sys.exit(FAIL)


if __name__ == "__main__":
    main()
    sys.exit(SUCCESS)
