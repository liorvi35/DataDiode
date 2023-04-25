import Sender

with open("file", "rb") as f1, open("tmp_p2", "rb") as f2:

    print(Sender.encrypt_file(f1) == Sender.encrypt_file(f2))
