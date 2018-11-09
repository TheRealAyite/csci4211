import socket

def createConnection():
    localhost = '127.0.0.1'
    port = 8080
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((localhost, port))
    s.listen(5)

    connection, addr = s.accept()
    print("Connection from " + str(addr))
    while True:
        data = connection.recv(1024)
        if not data:
            print("No data")
            break
        print("Data from user: " + str(data))
        #TODO: Comeback and fix this.
        connection.send(data)
        params = str(data).split(' ')
        client_id = params[0]
        clients_list = []
        if client_id not in clients_list:
            clients_list.append(client_id)
        host_name = params[1]
        query_type = params[2]
    connection.close()

if __name__ == "__main__":
    createConnection()
