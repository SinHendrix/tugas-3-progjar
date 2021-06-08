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

def check_friend_list():
    pass

def specify_receiver():
    return input("Masukkan username tujuan (ketikkan bcast untuk broadcast):")

def send_message():
    dest = specify_receiver()
    sock_cli.send(bytes("{}|{}".format(dest, msg), settings.ENCODING))

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
    username = header_datas[4]

    print("Receiving file from {}".format(username))

    with open(settings.FILE_ROUTE_RECEIVE + file_name, "wb") as file:
        while received_size < file_size:
        # while True:
            # data = sock_cli.recv(settings.BATCH_SIZE)
            data = sock_cli.recv(settings.BATCH_SIZE)
            received_size += len(data)

            # if not data:
            #     break


            file.write(data)

def read_msg(sock_cli):
    while True:
        message_header = get_message_header(sock_cli)

        if len(message_header) == 0:
            break

        header_datas = message_header.split("|")

        if header_datas[0] == "friend-list":
            pass
        elif header_datas[0] == "message":
            pass
        elif header_datas[0] == "file":
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
    2. Kirim Pesan
    3. Kirim File
    4. Exit
    """)

    try:
        cmd = int(input("Masukkan angka command anda: "))
    except Exception as e:
        print("Command yang dimasukkan salah")
        continue

    if cmd == 1:
        check_friend_list()
    elif cmd == 2:
        send_message()
    elif cmd == 3:
        send_file()
    elif cmd == 4:
        sock_cli.close()
        break
    else:
        print("Command yang dimasukkan salah")
        continue
