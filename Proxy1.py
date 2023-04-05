"""
this file contains the implementation for proxy1, second entity in data flow (2/5)
:version: 1.2
:date: 05/24/2023
:authors: Lior Vinman & Yoad Tamar
"""

import os
import socket

NEW_FILE_NAME = "./secret"  # name for temporary file with encryption
PROXY1_ADDR = ("127.0.0.1", 61947)  # IPv4 address and port of proxy1
DATA_DIODE_ADDR = ("127.0.0.1", 61948)  # IPv4 address and port of the data-diode
NUM_CONN = 200  # max number of TCP-clients
CHUNK_SIZE = 1024  # reading and writing files in chunks of 1KB


def send_file(file):
    """
    this function opens a UDP socket and sends a file through it
    :param file: file to send
    """
    try:
        proxy1_udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # opening UDP socket
        chunk = file.read(CHUNK_SIZE)  # reading file chunk
        while chunk:
            proxy1_udp_sock.sendto(chunk, DATA_DIODE_ADDR)  # sending chunks via socket
            chunk = file.read(CHUNK_SIZE)  # continuing reading
        # closing socket
        proxy1_udp_sock.shutdown(socket.SHUT_RDWR)
        proxy1_udp_sock.close()
    except socket.error:
        print("Error occurred, cannot create UDP socket")


def recv_file(sock):
    """
    this file receives a file from a TCP socket
    :param sock: file descriptor of a TCP socket
    """
    try:
        with open(NEW_FILE_NAME, "wb") as file:  # creating a new temporary file
            chunk = sock.recv(CHUNK_SIZE)  # receiving file in chunks
            while chunk:
                file.write(chunk)  # writing into temporary file
                chunk = sock.recv(1024)
    except socket.error:
        print("Cannot receive file.")
        exit(1)

def main():
    """
    main program flow:
    1- open a TCP socket
    2- get a connection from the sender
    3- receive the encrypted file
    4- open a UDP socket
    5- send the file to DataDiod via UDP socket
    6- delete temporary file & close sockets
    :return: 1 if there is an error, 0 else
    """
    try:
        proxy1_tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        proxy1_tcp_sock.bind(PROXY1_ADDR)
        proxy1_tcp_sock.listen(NUM_CONN)
    except socket.error:
        print("Error occurred, cannot open socket.")
        exit(1)

    while True:
        try:
            sender_tcp_sock, sender_addr = proxy1_tcp_sock.accept()
        except socket.error:
            print("Error occurred, cannot accept connection.")
            exit(1)

        recv_file(sender_tcp_sock)

        with open(NEW_FILE_NAME, "rb") as file:
            send_file(file)

        os.remove(NEW_FILE_NAME)
        sender_tcp_sock.close()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Shutting down first proxy server...")
        exit(0)


