import socket
import threading

def read_msg(clients, sock_cli, addr_cli, username_cli):
    while True:
        #accept message
        data = sock_cli.recv(65535)
        if len(data) == 0:
            break

        #parse the message
        dest, msg = data.decode("utf-8").split("|")
        msg = "<{}>: {}".format(username_cli, msg)

        #forward message to all clients
        if dest == "bcast":
            send_broadcast(clients, msg, addr_cli)
        else:
            dest_sock_cli = clients[dest][0]
            send_msg(dest_sock_cli, msg)
        print(data)
    sock_cli.close()
    print("Connection closed", addr_cli)

#send to all clients
def send_broadcast(clients, data, sender_addr_cli):
    for sock_cli, addr_cli, _ in clients.values():
        if not (sender_addr_cli[0] == addr_cli[0] and sender_addr_cli[1] == addr_cli[1]):
            send_msg(sock_cli, data)

def send_msg(sock_cli, data):
    sock_cli.send(bytes(data, "utf-8"))

#make object socket server
sock_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#bind socket to specific IP
sock_server.bind(("0.0.0.0", 6666))

#listen for incoming connection
sock_server.listen(5)

#dictionary for clients
clients = {}

while True:
    #accept connection from client
    sock_cli, addr_cli = sock_server.accept()

    #read username clients
    username_cli = sock_cli.recv(65535).decode("utf-8")
    print(username_cli, " joined")

    #make new thread to read the message
    thread_cli = threading.Thread(target=read_msg, args=(clients, sock_cli, addr_cli, username_cli))
    thread_cli.start()

    #save clients info to dictionary
    clients[username_cli] = (sock_cli, addr_cli, thread_cli)