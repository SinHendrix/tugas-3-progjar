import socket
import threading
import re
import settings

def get_message_header(sock_cli):
    message_header = ""
    while len(re.findall('\n', message_header)) < 4:
        data = sock_cli.recv(1).decode(settings.ENCODING)

        if len(data) == 0:
            return ""

        message_header += data

    return message_header

def receiving_and_sending_another_user(sock_cli, clients, sender_addr_cli, header_datas, username_cli, header, data_size):
    received_size = 0

    if header_datas[1] == "bcast":
        send_broadcast(clients, header, sender_addr_cli, username_cli)
    elif not check_if_friend(clients, header_datas, username_cli):
        message = "User yang dimaksud tidak ditemukan atau bukan merupanan teman"
        send_message_back(sock_cli, username_cli, message)
    else:
        send_msg(clients[header_datas[1]]['sock_cli'], header)

    while received_size < data_size:
        data = sock_cli.recv(settings.BATCH_SIZE)
        received_size += len(data)

        if header_datas[1] == "bcast":
            send_broadcast(clients, data, sender_addr_cli, username_cli)
        elif check_if_friend(clients, header_datas, username_cli) :
            send_msg(clients[header_datas[1]]['sock_cli'], data)

def file_sharing(sock_cli, clients, sender_addr_cli, header_datas, username_cli):
    data_size = int(header_datas[3])
    header = bytes(
            "|".join(header_datas[:4]) +
            "|" + username_cli +
            "|\n\n\n\n", settings.ENCODING)

    receiving_and_sending_another_user(sock_cli, clients, sender_addr_cli, header_datas, username_cli, header, data_size)

def message_sharing(sock_cli, clients, sender_addr_cli, header_datas, username_cli):
    data_size = int(header_datas[2])
    header = bytes(
            "|".join(header_datas[:3]) +
            "|" + username_cli +
            "|\n\n\n\n", settings.ENCODING)

    receiving_and_sending_another_user(sock_cli, clients, sender_addr_cli, header_datas, username_cli, header, data_size)

def check_if_friend(clients, header_datas, username_cli):
    if header_datas[1] not in clients[username_cli]['friend_list']:
        return False
    else:
        return True

def send_message_back(sock_cli, username_cli, message):
    message = bytes(message, settings.ENCODING)

    header = bytes(
            "|".join(['message', username_cli, str(len(message)), 'server', "\n\n\n\n"])
            , settings.ENCODING)

    send_msg(sock_cli, header)
    send_msg(sock_cli, message)

def get_friend_list(sock_cli, clients, sender_addr_cli, header_datas, username_cli):
    message = ""

    if len(clients[username_cli]['friend_list']) < 1:
        message = "Daftar teman Anda masih kosong"
    else :
        for username in clients[username_cli]['friend_list']:
            message += "- {}\n".format(username)
    send_message_back(sock_cli, username_cli, message)


def add_friend(sock_cli, clients, sender_addr_cli, header_datas, username_cli):
    message = ""
    friend_username = header_datas[1]

    if friend_username not in clients:
        message = "User tidak ditemukan"
    elif friend_username in clients[username_cli]['friend_list']:
        message = "User sudah menjadi teman"
    elif friend_username == username_cli:
        message = "Diri sendiri"
    else :
        clients[username_cli]['friend_list'].append(friend_username)
        clients[friend_username]['friend_list'].append(username_cli)
        message = "Penambahan teman berhasil"
    send_message_back(sock_cli, username_cli, message)

def read_msg(clients, sock_cli, addr_cli, username_cli):
    while True:
        #accept message header
        message_header = get_message_header(sock_cli)

        if len(message_header) == 0:
            break

        try:
            header_datas = message_header.split("|")

            if header_datas[0] == "friend-list":
                get_friend_list(sock_cli, clients, addr_cli, header_datas, username_cli)
            if header_datas[0] == "add-friend":
                add_friend(sock_cli, clients, addr_cli, header_datas, username_cli)
            elif header_datas[0] == "message":
                message_sharing(sock_cli, clients, addr_cli, header_datas, username_cli)
            elif header_datas[0] == "file":
                file_sharing(sock_cli, clients, addr_cli, header_datas, username_cli)
            elif header_datas[0] == "exit":
                break
        except Exception as e:
            send_message_back(sock_cli, username_cli, str(e))

    sock_cli.close()
    print("Connection closed ", addr_cli)

#send to all clients friends
def send_broadcast(clients, data, sender_addr_cli, username_cli):
    for friend in clients[username_cli]['friend_list']:
        if not (sender_addr_cli[0] == clients[friend]['addr_cli'][0] and sender_addr_cli[1] == clients[friend]['addr_cli'][1]):
            send_msg(clients[friend]['sock_cli'], data)

def send_msg(sock_cli, data):
    sock_cli.send(data)

#make object socket server
sock_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#bind socket to specific IP
sock_server.bind(("0.0.0.0", settings.port))

#listen for incoming connection
sock_server.listen(5)

#dictionary for clients
clients = {}

while True:
    #accept connection from client
    sock_cli, addr_cli = sock_server.accept()

    #read username clients
    username_cli = sock_cli.recv(settings.BATCH_SIZE).decode(settings.ENCODING)
    print(username_cli, " joined")

    #make new thread to read the message
    thread_cli = threading.Thread(target=read_msg, args=(clients, sock_cli, addr_cli, username_cli))
    thread_cli.start()

    #save clients info to dictionary
    clients[username_cli] = {
        'sock_cli': sock_cli,
        'addr_cli': addr_cli,
        'thread_cli': thread_cli,
        'friend_list': []
    }
