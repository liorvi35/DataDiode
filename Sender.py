"""
this file is implementation for the sender, first entity in data flow (1/5)
the sender is the part who encrypting the message (file) and sending
to the first proxy server using a TCP (Transmission Control Protocol) socket.

:version: 1.3
:since: 06.04.2023
:authors: Lior Vinman & Yoad Tamar
"""

import socket
import hashlib
import io
import sys
import os
import time
import tqdm

FIRST_PROXY_ADDR = ("127.0.0.1", 5060)  # address of first proxy server
NEW_FILE_NAME = "encrypt_sender"  # name for creation of a temporary file
CHUNK_SIZE = 1  # chunk size of receiving and sending file
TIMEOUT = 0.1  # timeout after each sending or receiving segment


def encrypt_file(file):
    """
    this function encrypts file using md5 encryption
    :param file: file descriptor of a file that should be encrypted
    :return: ciphertext of the message in md5 encryption
    """
    md5_enc = hashlib.md5()  # getting 'md5' encrypting format
    try:
        chunk = file.read(io.DEFAULT_BUFFER_SIZE)  # reading file segment
        while chunk:
            md5_enc.update(chunk)  # updating encryption in segments
            chunk = file.read(io.DEFAULT_BUFFER_SIZE)
    except IOError as e:
        print(f"[-] An error occurred while reading the file: {e}.")
        sys.exit(1)

    try:
        hex_rep = md5_enc.hexdigest()  # converting ciphertext to hexadecimal representation
        with open(NEW_FILE_NAME, "w") as file:
            file.write(hex_rep)
        return hex_rep
    except IOError as e:
        print(f"[-] An error occurred while creating the temporary file: {e}.")
        sys.exit(1)


def send_file(sock, file):
    """
    this function sends file (in segments) via socket
    :param sock: file descriptor of a socket to send through
    :param file: file descriptor of a file that should be sent
    """
    try:
        with tqdm.tqdm(total=(8 * os.path.getsize(NEW_FILE_NAME)), unit="b", unit_scale=True, desc="Sending") as pb:
            chunk = file.read(CHUNK_SIZE)  # reading file segment
            while chunk:
                sock.sendall(chunk)  # sending files over the socket in segments
                pb.update(len(8 * chunk))
                time.sleep(0.1)
                chunk = file.read(CHUNK_SIZE)
    except IOError as e:
        print(f"[-] An error occurred while reading the file: {e}.")
        sys.exit(1)


def main():
    try:
        with open(sys.argv[1], "rb") as file:  # selecting & encrypting file (step 'a')
            ciphertext = encrypt_file(file)
    except FileNotFoundError as e:
        print(f"[-] File not found: {e}.")
        sys.exit(1)
    except IndexError:
        print(f"[-] Usage: python3 {sys.argv[0]} <file-path>.")
        sys.exit(1)
    except IOError as e:
        print(f"[-] An error occurred while reading the file: {e}.")
        sys.exit(1)

    print(f"[+] File has been encrypted into: '{ciphertext}'.")

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as main_sock:
            main_sock.connect(FIRST_PROXY_ADDR)
            print("[+] Connection with 'proxy1' was established.")

            with open(NEW_FILE_NAME, "rb") as file:  # sending encrypted file to proxy 1 using TCP (step 'b')
                send_file(main_sock, file)

            os.remove(NEW_FILE_NAME)  # removing temporary file
            print("[+] File has been sent.")

            main_sock.shutdown(socket.SHUT_RDWR)

    except socket.error as e:
        print(f"[-] An error occurred while communicating with the socket: {e}.")
        sys.exit(1)


if __name__ == "__main__":
    main()
    sys.exit(0)
