import socket
import sys
from _thread import *


cache = {}

def loadCache(filename):
    file = open(filename, "r")
    for line in file:
        line = line.split(',')

        hostname = line[0]
        ip_address = line[1]
        cache[hostname] = ip_address
def writeError(message, client_id):
    file = open(client_id + ".log", "a")
    file.write(message + "\n")
    file.close()


def createConnection():
    localhost = '127.0.0.1'
    port = 8080
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        s.bind((localhost, port))
    except:
        print("Bind error")
        sys.exit()
    s.listen(5)

    # Resolve the queries.
    while True:
        connection, addr = s.accept()
        start_new_thread(newQuery, (connection,))
def resolveQuery(client_id, response, hostname, queryType):
    hostType = hostname.split('.')[2].lower()
    dnsIP = ""
    port = None
    if hostType == 'com':
        dnsIP = '192.168.1.101'
        port = 5678
    elif hostType == 'org':
        dnsIP = '192.168.1.102'
        port = 5679
    elif hostType == 'gov':
        dnsIP = '192.168.1.103'
        port = 5680
    else:
        #TODO: Logging/exit
        print("Invalid Query Type. Please enter .com .gov or .org for resolution")
        writeError(str(response), client_id)
        writeError("0xEE, default_local, Invalid format", client_id)
        sys.exit()

    if queryType.lower() == 'i':
        print("Iterative Query")

    elif queryType.lower() == "r":
        print("Recursive Query")
        print(dnsIP)
        print(port)
        s = socket.socket()
        try:
            s.connect((dnsIP, port))
        except:
            print("Failure to connect.")
            return "Hello"
            sys.exit()
        s.send("Recursive " + hostname)
        data = s.recv(2048)
        print("Received From Server: " + str(data.decode()))
        s.close()
    return "Hello"

def newQuery(connection):
    while True:
        data = connection.recv(1024)
        response = data.decode()
        if  not data:
            break
        print(response)
        #split the query string into separate parameters to get the parameters of the DNS query.
        try:
            params = str(response).split(',')
        except:
            print("Invalid Format!!")
            sys.exit()
            #TODO: Logging.

        try:
            client_id = params[0].replace(" ", "").lower()
            try:
                #open a log file...
                file = open(client_id + ".log", "a")
                print("File opened.")
                print("Client_ID: " + client_id)
            except:
                print("File does not exist")
        except:
            print("Invalid Format!!")
            #TODO: Logging.
            writeError(str(response), client_id)
            writeError("0xEE, default_local, Invalid format", client_id)
            sys.exit()

        try:
            host_name = params[1].replace(" ", "").lower()
            if host_name == "":
                print("Invalid host name. Please enter something valid.")
                #TODO LOGGING
                writeError(str(response), client_id)
                writeError("0xEE, default_local, Invalid Host", client_id)
            print("HOSTNAME: " + host_name)
        except:
            print("Invalid Format. No Hostname!!")
            writeError(str(response), client_id)
            writeError("0xEE, default_local, Invalid Host", client_id)
            #TODO: Logging.
        try:
            query_type = params[2].replace(" ", "").lower()
            print("QUERY_TYPE: " + query_type)
            if query_type == "":
                print("Invalid query type. Please enter something valid.")
                #TODO LOGGING
                writeError(str(response), client_id)
                writeError("0xEE, default_local, Invalid format", client_id)
            elif query_type != 'r' and query_type != 'i' :
                print("Invalid query type. Please enter something valid.")
                writeError(str(response), client_id)
                writeError("0xEE, default_local, Invalid format", client_id)
                #TODO LOGGING
            else: #Valid query
                try:
                    connection.send(cache[host_name].encode()) #send them the valid ip address in cache.
                except:
                    print("Query not previously resolved. Resolving.")
                    hello = resolveQuery(client_id,response, host_name, query_type)
                    print("Sending.......")
                    connection.send("hello".encode())
        except:
            print("Invalid Query type.")
            writeError(str(response), client_id)
            writeError("0xEE, default_local, Invalid format", client_id)

    connection.close()
def main():
    loadCache("cache.txt")
    createConnection()
    
if __name__ == "__main__":
    main()
