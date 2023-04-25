from cryptography.fernet import Fernet
import hashlib
import socket
import time
import tqdm
import sys
import io
import os

PRIVATE_ENCRYPTION_KEY = b"ic0-We1jiAx6pdWCe_72QxcFcZqhHwH3t46xeXPWONY="  # private key of fernet encryption (symmetric)
FIRST_PROXY_ADDR = ("127.0.0.1", 5060)  # server's address
BUFFER_SIZE = io.DEFAULT_BUFFER_SIZE  # buffer size of sending / receiving
TIMEOUT = 0.01  # waiting time after each send
SUCCESS = 0  # program's successful execution code
FAIL = 1  # program's failure execution code


def hash_file(file):
    """
    this function hashes file into MD5
    :param file: file object to hash
    :return: hexadecimal representation of file's MD5 hash
    """
    try:
        md5 = hashlib.md5()  # getting the MD5-hash object
        data = file.read(io.DEFAULT_BUFFER_SIZE)
        while data:  # reading all file, updating into MD5
            md5.update(data)
            data = file.read(io.DEFAULT_BUFFER_SIZE)
        file.seek(0)  # returning the file-pointer to beginning
        return md5.hexdigest()
    except Exception as e:
        print(f"Error: {e}.")
        sys.exit(FAIL)


def main():
    """
    this function is the main program, connecting to proxy1 and sending the file
    :return: FAIL(=1) on error, SUCCESS(=0) if file has been sent successfully
    """
    if len(sys.argv) != 2:  # checking arguments (file to send)
        print("Usage: 'python3 Sender.py <file>'.")
        sys.exit(FAIL)

    with open(sys.argv[1], "rb") as file:  # opening file, hashing into MD5
        ciphertext = hash_file(file)
        print(f"MD5 = '{ciphertext}'.")

        try:
            fernet = Fernet(PRIVATE_ENCRYPTION_KEY)  # creating encryption key
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP) as main_sock:
                main_sock.connect(FIRST_PROXY_ADDR)  # connecting to proxy1 and sending the file
                print(f"Established connection with: '{FIRST_PROXY_ADDR}'.")

                with tqdm.tqdm(total=os.path.getsize(sys.argv[1]), unit="B", unit_scale=True, desc="Sending") as pb:
                    data = file.read(BUFFER_SIZE)
                    while data:
                        encrypted = fernet.encrypt(data)  # encrypting data
                        main_sock.sendall(encrypted)
                        pb.update(len(data))
                        time.sleep(TIMEOUT)
                        data = file.read(BUFFER_SIZE)
                print("File has been sent.")

                main_sock.shutdown(socket.SHUT_RDWR)  # logging-out the sender from the connection
        except KeyboardInterrupt:
            print("\nClosing sender.")
            sys.exit(SUCCESS)
        except Exception as e:
            print(f"Error: {e}.")
            sys.exit(FAIL)
        finally:  # closing file and socket when exiting
            if main_sock:
                main_sock.close()
            if file:
                file.close()


if __name__ == "__main__":
    #print(Fernet.generate_key())

    main()
    sys.exit(SUCCESS)
