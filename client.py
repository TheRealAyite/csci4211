import socket

def createConnection():
    host = '127.0.0.1'
    port = 8080

    s = socket.socket()
    s.connect((host, port))

    message = input("Please enter you query. (CLIENT ID, HOSTNAME, I/R) separate the parameters by space: ")
    while message != 'q':
        s.send(message.encode())
        data = s.recv(1024)
        print("Received From Server: " + str(data.decode()))
        message = input("Please Enter Some Data: ")
    s.close()



if __name__ == "__main__":
    createConnection()
