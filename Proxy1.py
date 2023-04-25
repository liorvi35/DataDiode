from cryptography.fernet import Fernet
import socket
import time
import tqdm
import sys
import os
import io

PRIVATE_KEY_TCP = b"ic0-We1jiAx6pdWCe_72QxcFcZqhHwH3t46xeXPWONY="  # private key of fernet encryption (symmetric)
PRIVATE_KEY_RUDP = b"hWxUqsmILG8jzPljbsf-WDeHaOtM_B4c-PO8PZutWMk="
SECOND_PROXY_ADDR = ("127.0.0.1", 5061)  # server's address
FIRST_PROXY_ADDR = ("127.0.0.1", 5060)  # current address
BUFFER_SIZE = io.DEFAULT_BUFFER_SIZE  # buffer size of sending / receiving
TEMP_FILE_NAME = "p1"  # temporary filename for receiving file, real name: p1_clientAddr
SEND_REQ = b"N1:1:S"  # data-send request RUDP
WAITING = 0.01  # waiting time after each send
TIMEOUT = 5  # RUDP socket timeout for receiving data
SUCCESS = 0  # program's successful execution code
ACK = b"A"  # RUDP acknowledgment signal
FAIL = 1  # program's failure execution code
SPLITTER = b":"  # payload splitter
EMPTY_MESSAGE = b""  # last message in connection
MAX_CONNECTIONS = 300  # maximal number of TCP clients


def build_payload(final, seq, data):
    """
    this function build's the data of the RUDP packet that we'll send
    :param final: True if packet is last file segment, False else
    :param seq: packet sequence number in the send-order
    :param data: the data itself
    :return: payload in format - <N/F><Seq>:<length(Data)>:<Data>
    """
    ch = "F" if final else "N"
    return f"{ch}{seq}:{len(data)}:{data.decode()}".encode()


def check_recv(sock, packet):
    """
    this function checks the RUDP receive
    :param sock: socket to receive data from
    :param packet: data to send again in case of receive fail
    :return: (True,received-message) if successful, else (False,None)
    """
    sock.settimeout(TIMEOUT)
    while True:
        try:  # trying to receive up to timeout
            msg, address = sock.recvfrom(BUFFER_SIZE)
            sock.settimeout(None)
            return True, msg
        except (socket.timeout, socket.error):  # if timeout passed, we assume packet is lost
            sock.sendto(packet, SECOND_PROXY_ADDR)
            time.sleep(WAITING)
            continue
    sock.settimeout(None)
    return False, None


def send_file(addr):
    """
    this function sends a file using RUDP
    """
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as flow_sock:
        flow_sock.sendto(SEND_REQ, SECOND_PROXY_ADDR)  # sending send-request to server to start file transfer
        status, data = check_recv(flow_sock, SEND_REQ)
        if not status:
            sys.exit(FAIL)
        with open(f"{TEMP_FILE_NAME}_{addr}", "rb") as file:  # sending file
            with tqdm.tqdm(total=os.path.getsize(f"{TEMP_FILE_NAME}_{addr}"),
                           unit="B", unit_scale=True, desc="Sending") as pb:
                seq = 2
                data = file.read(BUFFER_SIZE)
                while data:
                    flow_sock.sendto(build_payload(False, seq, data), SECOND_PROXY_ADDR)
                    status, to_send = check_recv(flow_sock, build_payload(False, seq, data))
                    if not status:  # if not received
                        sys.exit(FAIL)
                    if int(to_send.split(SPLITTER)[1].decode()) != seq:  # if received packet with wrong sequence
                        ack = int(to_send.split(SPLITTER)[1].decode())
                        file.seek(0)
                        file.read(ack)
                        seq = ack + 1
                        data = file.read(BUFFER_SIZE)
                        continue
                    pb.update(len(data))
                    time.sleep(WAITING)
                    data = file.read(BUFFER_SIZE)
                    seq += 1
                flow_sock.sendto(build_payload(True, seq, EMPTY_MESSAGE), SECOND_PROXY_ADDR)
                status, data = check_recv(flow_sock, build_payload(True, seq, EMPTY_MESSAGE))
                if data != ACK:
                    sys.exit(FAIL)


def main():
    """
    this function is the main program, accepting connection from sender then sending file to proxy2
    :return: FAIL(=1) on error, SUCCESS(=0) if file has been sent successfully
    """
    try:
        fernet = Fernet(PRIVATE_KEY_TCP)  # creating encryption key
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP) as main_sock:
            main_sock.bind(FIRST_PROXY_ADDR)  # binding on address
            main_sock.listen(MAX_CONNECTIONS)  # listening for connections
            print("Listening for incoming connections...")

            while True:
                client_sock, client_addr = main_sock.accept()
                with open(f"{TEMP_FILE_NAME}_{client_addr}", "wb") as file:
                    with tqdm.tqdm(total=None, unit="B", unit_scale=True, desc="Receiving") as pb:
                        data = client_sock.recv(io.DEFAULT_BUFFER_SIZE)  # receiving file
                        while data:
                            decrypted = fernet.decrypt(data)  # decrypting data
                            file.write(decrypted)
                            pb.update(len(data))
                            time.sleep(WAITING)
                            data = client_sock.recv(io.DEFAULT_BUFFER_SIZE)
                    print("File has been received.")

                send_file(client_addr)  # sending file
                print("File has been sent.")

                os.remove(f"{TEMP_FILE_NAME}_{client_addr}")  # deleting temporary file after send
    except KeyboardInterrupt:
        print("\nClosing proxy1.")
        sys.exit(SUCCESS)
    except Exception as e:
        print(f"Error: {e}.")
        sys.exit(FAIL)


if __name__ == "__main__":
    main()
