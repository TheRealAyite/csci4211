import socket
import sys
from _thread import *

cache = {}
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

root_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
root_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

org_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
org_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

gov_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
gov_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

com_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
com_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

localhost = '127.0.0.1'
port = 5352

try:
    s.bind((localhost, port))
except:
    print("Bind Error")
    sys.exit(1)
s.listen(5)

try:
    root_sock.bind((localhost, 5353))
except:
    print("Bind Error")
    sys.exit(1)

root_sock.listen(5)

try:
    org_sock.bind((localhost, 5354))
except:
    print("Bind Error")
    sys.exit(1)

org_sock.listen(5)

try:
    gov_sock.bind((localhost, 5355))
except:
    print("Bind Error")
    sys.exit(1)

gov_sock.listen(5)

try:
    com_sock.bind((localhost, 5356))
except:
    print("Bind Error")
    sys.exit(1)

com_sock.listen(5)

root_client = socket.socket()

def load_mapping(tld):
    mapping = {}
    if tld == 'org':
        file_name = 'org.dat'
    elif tld == 'gov':
        file_name = 'gov.dat'
    else:
        file_name = 'com.dat'
    file = open(file_name, "r")
    for line in file:
        line = line.split(' ')

        hostname = line[0].lower()
        if 'www' not in hostname:
            hostname = 'www.' + hostname
        ip_address = line[1]
        mapping[hostname] = ip_address
    return mapping
def load_cache(filename):
    file = open(filename, "r")
    for line in file:
        line = line.split(',')

        hostname = line[0]
        ip_address = line[1]
        cache[hostname] = ip_address

def log_query(message, client_id):
    file = open(client_id + ".log", "a")
    file.write(message + "\n")
    file.close()

def log_error(message, client_id):
    file = open(client_id + ".log", "a")
    file.write(message + "\n")
    file.close()

def start_server():
    # Start the threads for the root, org com and gov servers....
    start_new_thread(org_server, (org_sock,))
    start_new_thread(gov_server, (gov_sock,))
    start_new_thread(com_server, (gov_sock,))

    while True:
        print("In This Loop...Aceept")
        connection, addr = s.accept()
        start_new_thread(new_query, (connection,))
def com_server(socket):
    connection, addr = socket.accept()
    mapping = load_mapping('com')
    print(str(mapping) + " For com\n")
    while True:
        data = connection.recv(1024)
        request = data.decode()
        if  not data:
            break
        print("Received From Client (com): " + request + "\n")
        connection.send(mapping[request].encode())
def gov_server(socket):
    connection, addr = socket.accept()
    mapping = load_mapping('gov')
    print(str(mapping) + " For gov\n")

    while True:
        data = connection.recv(1024)
        request = data.decode()
        if "www" not in request:
            request = "www." + request
        print(request)
        if  not data:
            break
        print("Received From Client (gov): " + request + "\n")
        connection.send(mapping[request].encode())
def org_server(socket):
    connection, addr = socket.accept()
    mapping = load_mapping('org')
    print(str(mapping) + " For org\n")
    while True:
        data = connection.recv(1024)
        request = data.decode()
        if "www" not in request:
            request = "www." + request
        if  not data:
            break
        print("Received From Client (org): " + request + "\n")
        try:
            connection.send(mapping[request].encode())
        except:
            print("0xFF, org, Host not found")
            #TODO....LOG IT
            connection.send("0xFF, org, Host not found".encode())
def root_server(socket, client_socket):
    print("Request received by root_server")
    connection, addr = socket.accept()
    count = 0
    localhost = '127.0.0.1'
    print(localhost)
    while True:
        print("This is still working" + str(count))
        data = connection.recv(102400)
        print("Yuppp" + str(count))
        request = data.decode()
        print("This is the request: " + request)
        if  not data:
            break
        #TODO: Received request.....log.
        params = str(request).split(',')
        client_id = params[0].lower().replace(" ", "")
        host_name = params[1].lower().replace(" ", "")
        query_type = params[2].lower().replace(" ", "")

        try:
            hostType = host_name.split('.')[2].lower()
        except:
            hostType = host_name.split('.')[1].lower()

        print("TLD: " + hostType)
        print("HOSTNAME: " + host_name)

        if query_type == "r":
            #Find the tld server to contact....com gov or org....
            print("Recursive Query Root.")
            if hostType == 'org':
                #Connect to org server....
                try:
                    client_socket.connect((localhost, 5354)) #Connect to the org server....
                except:
                    print("Failed connection. Server_Stuff..org")
                client_socket.send(host_name.encode())
                while True:
                    data = client_socket.recv(1024)
                    print("Received From Server: " + str(data.decode()))
                    #Connect to the local dns server....
                print("Never stops...")
                try:
                    client_socket.connect((localhost, 5352)) #Connect to the org server....
                except:
                    print("Failed connection. Server_Stuff..org. 2")
                client_socket.send(data)
            elif hostType == 'gov':
                try:
                    client_socket.connect((localhost, 5355)) #Connect to the gov server....
                except:
                    print("Failed connection. Server_Stuff..Gov")
                client_socket.send(host_name.encode())
                while True:
                    data = client_socket.recv(1024)
                    print("Received From Server: " + str(data.decode()))
            elif hostType == 'com':
                try:
                    client_socket.connect((localhost, 5356)) #Connect to the com server....
                except:
                    print("Failed connection. Server_Stuff...Com")
                client_socket.send(host_name.encode())
                while True:
                    data = client_socket.recv(1024)
                    print("Received From Server: " + str(data.decode()))
            else:
                print("Invalid TLD")
                connection.send("Invalid TLD".encode())               
            count += 1
        else: #Iterative query....
            #Send them infor for the correct server....
            print("Iterative query")
        print("Received From Client(root): " + request + "\n")
def resolve_query(client_id, response, hostname, queryType, connection):
    localhost = '127.0.0.1'
    start_new_thread(root_server, (root_sock,root_client))
    local_sock = socket.socket()
    try:
        local_sock.connect((localhost, 5353)) #Connect to the root server....
    except:
        print("Failed connection")
    local_sock.send(response.encode())
    print("Sent to the root server")

    #TODO: Receive a Response from the root server....
    while True:
        print("Testing....")
        data = connection.recv(1024)
        response = data.decode()
        if  not data:
            break
        print("Received from Root: " +  response)    

def new_query(connection):
    while True:
        data = connection.recv(1024)
        response = data.decode()
        if  not data:
            break
        print(response)

        try: #split the query string into separate parameters to get the parameters of the DNS query.
            params = str(response).split(',')
            print(params)
        except:
            print("Invalid Format!!")
            sys.exit(1)
            #TODO: Loggingself.
        print(params)
        client_id = params[0].lower().replace(" ", "")
        host_name = params[1].lower().replace(" ", "")
        if 'www' not in host_name:
            host_name = 'www.' + host_name
        print("New Hostname: " + host_name)
        query_type = params[2].lower().replace(" ", "")

        print(query_type)

        if query_type != "r" and query_type != "i":
            print("Invalid Query Type")
            log_query(response, client_id)
            log_error("0xEE, default_local, Invalid format",client_id)
            connection.send("0xEE, default_local, Invalid format".encode())
            sys.exit(1) #Exit the program......

        try:
            connection.send(cache[host_name].encode()) #send them the valid ip address in cache.
        except KeyError:
            print("Query not previously resolved. Resolving.")
            hello = resolve_query(client_id,response, host_name, query_type, connection)
            print("Sending.......")
            connection.send("hello".encode())
    connection.close()
def main():
    load_cache("cache.txt")
    start_server()
if __name__ == "__main__":
    main()
