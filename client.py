import socket
import sys
import threading

def read_msg(sock_cli):
    while True:
        #receive message
        data = sock_cli.recv(65535)
        if len(data) == 0:
            break
        print(data)

#make object socket
sock_cli = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#connect to server
sock_cli.connect(("127.0.0.1", 6666))

#send username to server
sock_cli.send(bytes(sys.argv[1], "utf-8"))

#make thread to read message 
thread_cli = threading.Thread(target=read_msg, args=(sock_cli,))
thread_cli.start()

while True:
    #send/receive message
    dest = input("masukkan username tujuan (ketikkan bcast untuk broadcast):")
    msg = input("Masukkan pesan anda: ")

    if msg == "exit":
        sock_cli.close()
        break

    sock_cli.send(bytes("{}|{}".format(dest, msg), "utf-8"))