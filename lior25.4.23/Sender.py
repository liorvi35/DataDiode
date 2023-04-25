import hashlib
import io
import os
import socket
import sys
import time
import tqdm

FIRST_PROXY_ADDR = ("127.0.0.1", 12345)
FAIL = 1
SUCCESS = 0
TIMEOUT = 0.01


def encrypt_file(file):
    try:
        md5 = hashlib.md5()
        data = file.read(io.DEFAULT_BUFFER_SIZE)
        while data:
            md5.update(data)
            data = file.read(io.DEFAULT_BUFFER_SIZE)
        file.seek(0)
        return md5.hexdigest()
    except (NameError, AttributeError, TypeError, IOError,
            OSError, FileNotFoundError, PermissionError) as e:
        print(f"[-] Error: {e}.")
        sys.exit(FAIL)


def main():
    if len(sys.argv) != 2:
        print("[-] Usage: 'python3 Sender.py <file>'.")
        sys.exit(FAIL)

    with open(sys.argv[1], "rb") as file:
        ciphertext = encrypt_file(file)
        print(f"[+] MD5 of file is: '{ciphertext}'.")

        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP) as sock:
                sock.connect(FIRST_PROXY_ADDR)
                print(f"[+] Connected to: {FIRST_PROXY_ADDR}.")

                with tqdm.tqdm(total=os.path.getsize(sys.argv[1]), unit="B", unit_scale=True, desc="Sending") as pb:
                    data = file.read(io.DEFAULT_BUFFER_SIZE)
                    while data:
                        sock.sendall(data)
                        pb.update(len(data))
                        time.sleep(TIMEOUT)
                        data = file.read(io.DEFAULT_BUFFER_SIZE)
                print(f"[+] File has been sent.")

                sock.shutdown(socket.SHUT_RDWR)
        except (socket.error, socket.timeout, ConnectionRefusedError, OSError, IOError) as e:
            print(f"[-] Error: {e}.")
            sys.exit(FAIL)
        except KeyboardInterrupt:
            print("\n[-] Closing...")
            sys.exit(SUCCESS)
        finally:
            if sock:
                sock.close()


if __name__ == "__main__":
    main()
