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

def file_sharing(sock_cli, clients, sender_addr_cli, header_datas, username_cli):
    received_size = 0
    file_size = int(header_datas[3])

    if header_datas[1] == "bcast":
        send_broadcast(clients, bytes(
            "|".join(header_datas[:4]) +
            "|" + username_cli +
            "|\n\n\n\n", settings.ENCODING),
        sender_addr_cli)

    # while True:
    while received_size < file_size:
        data = sock_cli.recv(settings.BATCH_SIZE)
        received_size += len(data)

        # if not data:
            # break

        if header_datas[1] == "bcast":
            send_broadcast(clients, data, sender_addr_cli)


def read_msg(clients, sock_cli, addr_cli, username_cli):
    while True:
        #accept message header
        message_header = get_message_header(sock_cli)

        if len(message_header) == 0:
            break

        header_datas = message_header.split("|")

        if header_datas[0] == "friend-list":
            pass
        elif header_datas[0] == "message":
            pass
        elif header_datas[0] == "file":
            file_sharing(sock_cli, clients, addr_cli, header_datas, username_cli)
        else:
            break

    sock_cli.close()
    print("Connection closed", addr_cli)

#send to all clients
def send_broadcast(clients, data, sender_addr_cli):
    for sock_cli, addr_cli, _ in clients.values():
        if not (sender_addr_cli[0] == addr_cli[0] and sender_addr_cli[1] == addr_cli[1]):
            send_msg(sock_cli, data)

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
    clients[username_cli] = (sock_cli, addr_cli, thread_cli)
