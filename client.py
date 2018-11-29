import socket
from _thread import *
from time import sleep

def listen(socket):
    while True:
        data = socket.recv(2048)
        response = data.decode()
        if  not data:
            break
        print(response + "\n")
def createConnection():
    host = '127.0.0.1'
    port = 5352

    s = socket.socket()
    s.connect((host, port))

    message = input("Please enter you query. (CLIENT ID, HOSTNAME, I/R) separate the parameters by comma. No need for parens: ")
    while message != 'q':
        s.send(message.encode())
        while True:
            start_new_thread(listen, (s,))
            sleep(1)
            break
        message = input("Please Enter A Query: ")
    s.close()



if __name__ == "__main__":
    createConnection()
