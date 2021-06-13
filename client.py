import socket
import sys
import threading
import os
import re
import settings

#make object socket
def file_exists(file_route):
    if not os.path.exists(file_route):
        print("File tidak ditemukan")
        return False
    return True

def specify_receiver():
    return input("Masukkan username tujuan (ketikkan bcast untuk broadcast):")

def friend_list():
    sock_cli.send(bytes("|".join(['friend-list', "\n\n\n\n"]), settings.ENCODING))

def add_friend():
    friend_name = input("Masukkan nama teman : ")
    sock_cli.send(bytes("|".join(['add-friend', friend_name, "\n\n\n\n"]), settings.ENCODING))

def client_exit():
    sock_cli.send(bytes("|".join(['exit', "\n\n\n\n"]), settings.ENCODING))
    sock_cli.close()

def send_message_command():
    dest = specify_receiver()
    message = input("Masukkan pesan : ")
    message = bytes(message, settings.ENCODING)

    sock_cli.send(bytes("|".join(['message', dest, str(len(message)), "\n\n\n\n"]), settings.ENCODING))
    sock_cli.send(message)

def get_file_name():
    while True:
        file_name = input("Masukkan Nama File : ")

        if file_exists(settings.FILE_ROUTE_DATASET + file_name):
            return file_name

def send_file():
    dest = specify_receiver()
    file_name = get_file_name()
    file_route = settings.FILE_ROUTE_DATASET + file_name
    file_handler = open(file_route,'rb')
    data = file_handler.read()
    file_size = os.stat(file_route).st_size

    sock_cli.send(bytes("file|{}|{}|{}|\n\n\n\n".format(dest, file_name, file_size), settings.ENCODING))

    sock_cli.sendall(data)
    file_handler.close()

def get_message_header(sock_cli):
    message_header = ""
    while len(re.findall('\n', message_header)) < 4:
        data = sock_cli.recv(1).decode(settings.ENCODING)

        if len(data) == 0:
            return ""

        message_header += data

    return message_header

def recv_file(sock_cli, header_datas):
    received_size = 0
    file_name = header_datas[2]
    file_size = int(header_datas[3])
    sender_name = header_datas[4]

    print("\nReceiving file from {}".format(sender_name))

    with open(settings.FILE_ROUTE_RECEIVE + file_name, "wb") as file:
        while received_size < file_size:
            data = sock_cli.recv(settings.BATCH_SIZE)
            received_size += len(data)

            file.write(data)

def recv_message(sock_cli, header_datas):
    received_size = 0
    msg_size = int(header_datas[2])
    sender_name = header_datas[3]
    message = ""

    print("\nReceiving message from {}".format(sender_name))

    while received_size < msg_size:
        data = sock_cli.recv(settings.BATCH_SIZE)
        received_size += len(data)
        message += data.decode(settings.ENCODING)

    print(message)

def read_msg(sock_cli):
    while True:
        message_header = get_message_header(sock_cli)

        if len(message_header) == 0:
            break

        header_datas = message_header.split("|")

        if header_datas[0] == "message":
            # header "message|dest|msg_size|sender_username|\n\n\n\n"
            recv_message(sock_cli, header_datas)
        elif header_datas[0] == "file":
            # header "file|dest|file_name|file_size|sender_username|\n\n\n\n"
            recv_file(sock_cli, header_datas)

sock_cli = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#connect to server
sock_cli.connect(("127.0.0.1", settings.port))

#send username to server
sock_cli.send(bytes(sys.argv[1], settings.ENCODING))

#make thread to read message
thread_cli = threading.Thread(target=read_msg, args=(sock_cli,))
thread_cli.start()

while True:
    #send/receive message
    print("""
    Command :
    1. Cek Friend List
    2. Tambah Friend
    3. Kirim Pesan
    4. Kirim File
    5. Exit
    """)

    try:
        cmd = int(input("Masukkan angka command anda: "))
    except Exception as e:
        print("Command yang dimasukkan salah")
        continue

    if cmd == 1:
        # header "friend-list|dest|msg_size|\n\n\n\n"
        friend_list()
    elif cmd == 2:
        # header "add-friend|dest|msg_size|\n\n\n\n"
        add_friend()
    elif cmd == 3:
        # header "message|dest|msg_size|\n\n\n\n"
        send_message_command()
    elif cmd == 4:
        # header "file|dest|file_name|file_size|\n\n\n\n"
        send_file()
    elif cmd == 5:
        # header "exit|\n\n\n\n"
        client_exit()
        break
    else:
        print("Command yang dimasukkan salah")
        continue
