"""
this file contains the implementation for sender, first entity in data flow (1/5)
:version: 1.1
:date: 05/24/2023
:authors: Lior Vinman & Yoad Tamar
"""

import hashlib
import socket
import sys
import os

NEW_FILE_NAME = "./secret"  # name for temporary file with encryption
PROXY1_ADDR = ("127.0.0.1", 61947)  # IPv4 address and port of proxy1
CHUNK_SIZE = 1024  # reading and writing files in chunks of 1KB


def encrypt_md5(file):
    """
    this function encrypts a file in md5 format
    :param file: file to encrypt
    """
    md5_enc = hashlib.md5()  # getting md5 encryption
    chunk = file.read(CHUNK_SIZE)  # reading chunks of file
    while chunk:
        md5_enc.update(chunk)  # encrypting chunk we read
        chunk = file.read(CHUNK_SIZE)  # reading another chunk
    hex_rep = md5_enc.hexdigest()  # converting the result into hexadecimal representation
    with open(NEW_FILE_NAME, "w") as output:
        output.write(hex_rep)  # saving the result into new file (that we'll send)


def send_file(sock, file):
    """
    this function sends a file via socket
    :param sock: TCP socket file descriptor
    :param file: file to send
    """
    chunk = file.read(CHUNK_SIZE)  # reading chunk of file
    while chunk:
        sock.sendall(chunk)  # sending the chunk
        chunk = file.read(CHUNK_SIZE)  # continuing reading the file


def main():
    """
    main program flow:
    1- encrypt the given file
    2- open a TCP connection with proxy1
    3- send the encrypted file to proxy1 via TCP socket
    4- cleanup: cleaning the files that has been created while reading
    5- closing connection with proxy1
    :return:
    """
    try:
        with open(f"{sys.argv[1]}", "rb") as file:
            encrypt_md5(file)
    except IndexError:
        print("Please provide path to file, usage: 'python3 Sender.py <path>'.")
        exit(1)
    except FileNotFoundError:
        print("Please make sure that path to file is correct.")
        exit(1)

    try:
        sender_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sender_sock.connect(PROXY1_ADDR)
    except socket.error:
        print("Cannot connect, please make sure that 'proxy1' is online.")
        exit(1)

    with open(NEW_FILE_NAME, "rb") as file:
        send_file(sender_sock, file)
    os.remove(NEW_FILE_NAME)

    sender_sock.shutdown(socket.SHUT_RDWR)
    sender_sock.close()


if __name__ == "__main__":
    main()
