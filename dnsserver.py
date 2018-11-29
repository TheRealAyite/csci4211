import socket
import sys
from _thread import *
import atexit

cache = {}

#Create sockets for the 5 servers.....

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

#read the server.dat file......

try:
    s.bind((localhost, port))
except:
    print("Bind Error")
    sys.exit(1)
s.listen(5)

try:
    root_sock.bind((localhost, 5353)) #create root server
except:
    print("Bind Error")
    sys.exit(1)

root_sock.listen(5)

try:
    org_sock.bind((localhost, 5354)) #create org server
except:
    print("Bind Error")
    sys.exit(1)

org_sock.listen(5)

try:
    gov_sock.bind((localhost, 5355)) #create gov server
except:
    print("Bind Error")
    sys.exit(1)

gov_sock.listen(5)

try:
    com_sock.bind((localhost, 5356)) #create com server
except:
    print("Bind Error")
    sys.exit(1)

com_sock.listen(5)

root_client = socket.socket() #this will be the client socket for the root server. Used to forward queries to org com gov servers and local server

def load_mapping(tld): #load in the mapping for each of the servers
    mapping = {}
    if tld == 'org':
        file_name = 'org.dat'
    elif tld == 'gov':
        file_name = 'gov.dat'
    else:
        file_name = 'com.dat'

    file = open(file_name, "r")

    for line in file: #split the ip addresses from the hostname.....create a dictionary for easier access
        line = line.split(' ')

        hostname = line[0].lower().replace(" ", "")
        if 'www' not in hostname:
            hostname = 'www.' + hostname
        ip_address = line[1]
        mapping[hostname] = ip_address

    return mapping

def load_cache(filename): #load the global cache
    file = open(filename, "r")

    for line in file:
        line = line.split('/')
        if line == ['\n']: #ignore new line characters
            pass
        else:
            hostname = line[0]
            ip_address = line[1]
            cache[hostname] = ip_address

def log_query(message, client_id): #log a query from a client ID
    file = open(client_id + ".log", "a")
    file.write(message + "\n")
    file.close()

def log_response(message, client_id): #log a response from a client ID
    file = open(client_id + ".log", "a")
    file.write(message + "\n")
    file.close()

def log_error(message, client_id): #log an error from a client ID
    file = open(client_id + ".log", "a")
    file.write(message + "\n")
    file.close()

def log_local(message): #log quries to the local dns server
    file = open("default_local" + ".log", "a")
    file.write(message + "\n")
    file.close()

def cache_response(message): #cache the response to a text file
    file = open("cache" + ".txt", "a")
    file.write(message)
    file.close()

def com_server(socket): #same as org and gov servers.....kept 3 methods for easier readbility than one
    connection, addr = socket.accept()

    mapping = load_mapping('com')

    print(str(mapping) + " For com\n")

    while True:
        data = connection.recv(1024)
        request = data.decode()

        if "www" not in request:
            request = "www." + request

        if  not data:
            break

        print("Received From Client (com): " + request + "\n")

        try:
            connection.send("0x00, com, ".encode() + mapping[request].encode()) #check the mapping and send the correct ip address to the requester.
            log_local("0x00, com, " + mapping[request] + "\n\n") #log the request to local
        except:
            print("0xFF, com, Host not found")
            log_local("0xFF, com, Host not found\n\n")
            connection.send("0xFF, com, Host not found".encode()) #Invalid query...send the response to the root server
            print("Sent to the root server")
            break
    connection.close()

def gov_server(socket): #same as com and org servers.....kept 3 methods for easier readbility than one
    connection, addr = socket.accept()

    mapping = load_mapping('gov')


    while True:
        data = connection.recv(1024)
        request = data.decode()

        if "www" not in request:
            request = "www." + request

        if  not data:
            break

        print("Received From Client (gov): " + request + "\n")

        try:
            connection.send("0x00, gov, ".encode() + mapping[request].encode())
            log_local("0x00, gov, " + mapping[request] + "\n\n") #check the mapping and send the correct ip address to the requester.
        except:
            print("0xFF, gov, Host not found")
            connection.send("0xFF, gov, Host not found".encode())
            log_local("0xFF, gov, Host not found\n\n")
            print("Sent to the root server")
    connection.close()

def org_server(socket): #same as com and gov servers.....kept 3 methods for easier readbility than one
    connection, addr = socket.accept()

    mapping = load_mapping('org')

    while True:
        data = connection.recv(1024)
        request = data.decode()
        if "www" not in request:
            request = "www." + request

        if  not data:
            break

        print("Received From Client (org): " + request + "\n")

        try:
            connection.send("0x00, org, ".encode() + mapping[request].encode())
            log_local("0x00, org, " + mapping[request] + "\n\n") #check the mapping and send the correct ip address to the requester.

        except:
            print("0xFF, org, Host not found")
            connection.send("0xFF, org, Host not found".encode())
            print("Sent to the root server")
            log_local("0xFF, org, Host not found\n\n")

    connection.close()
def root_server(socket, client_socket):
    start_new_thread(org_server, (org_sock,)) #start the org server....
    start_new_thread(gov_server, (gov_sock,)) #start the gov server....
    start_new_thread(com_server, (com_sock,)) #start the com server....

    connection, addr = socket.accept()
    localhost = '127.0.0.1'
    while True:
        data = connection.recv(1024)
        request = data.decode()

        print(request)
        print("Split: " + str(request.split(" ")))

        domain = request.split(" ")[0] #get the domain from the request the user input

        try:
            query_type = request.split(" ")[1] #get query type
        except:
            print("No query type specified")

        if  not data:
            break

        if query_type == "r":
            #Route to correct server.....gov com or org
            tld = find_tld(domain)
            if tld == 'org': #Contact the org_server....

                try:
                    client_socket.connect((localhost,5354)) #connecto to the org server
                    print("Connected to the client socket")
                except OSError as ex:
                    print("Failed to connect to the client socket")
                    print(ex)

                client_socket.send(domain.encode()) #Send request to the org Server
                print("Sent request to org socket")

                while True: #listen for a response from the org_server
                    response = client_socket.recv(1024).decode()
                    print("Recevied From TLD SERVER: " + response)
                    connection.send(response.encode())
                    print("Sent response to the local dns server....")

            elif tld == 'gov':

                try:
                    client_socket.connect((localhost,5355))
                    print("Connected to the client socket")
                except OSError as ex:
                    print("Failed to connect to the client socket")
                    print(ex)

                client_socket.send(domain.encode()) #Send request to the gov Server
                print("Sent request to gov socket")

                while True:
                    response = client_socket.recv(1024).decode()
                    print("Recevied From TLD SERVER: " + response)
                    connection.send(response.encode())
                    print("Sent response to the local dns server....")

            elif tld == 'com':

                try:
                    client_socket.connect((localhost,5356))
                    print("Connected to the client socket")
                except OSError as ex:
                    print("Failed to connect to the client socket")
                    print(ex)

                client_socket.send(domain.encode()) #Send request to the com Server
                print("Sent request to com socket")

                while True:
                    response = client_socket.recv(1024).decode()
                    print("Recevied From TLD SERVER: " + response)
                    connection.send(response.encode())
                    print("Sent response to the local dns server....")

            else: #invalid TLD.....
                connection.send("0xEE, default_local, Invalid format".encode())
        elif query_type == "i":
            #Iterative query.....
            tld = find_tld(domain)
            if tld == 'org':
                # Send IP of org server to the local dns server.....
                connection.send('127.0.0.1:5354'.encode())
                log_local("0x01, ROOT, 127.0.0.1, 5354")

            elif tld == 'gov': # Send IP of gov server to the local dns server.....
                connection.send('127.0.0.1:5355'.encode())
                log_local("0x01, ROOT, 127.0.0.1, 5355")

            elif tld == 'com': # Send IP of com server to the local dns server.....
                connection.send('127.0.0.1:5356'.encode())
                log_local("0x01, ROOT, 127.0.0.1, 5356")

def check_if_valid_query(request):
    try: #split the query string into separate parameters to get the parameters of the DNS query.
        params = str(request).split(',')
        print(params)
    except:
        print("Invalid Format!!")
        return (False)
        sys.exit(1)
    print(params)
    try:
        client_id = params[0].lower().replace(" ", "")
    except:
        return (False)

    try:
        host_name = params[1].lower().replace(" ", "")
    except:
        return (False)

    if 'www' not in host_name:
        host_name = 'www.' + host_name
    print("New Hostname: " + host_name)
    try:
        query_type = params[2].lower().replace(" ", "")
    except:
        return (client_id,host_name,False)
    print(query_type)

    if query_type != "r" and query_type != "i":
        print("Invalid Query Type")
        log_query(request, client_id)
        log_error("0xEE, default_local, Invalid format",client_id)
        return (False)
    valid_tld = find_tld(host_name)
    if valid_tld == False:
        return (False)
    return (client_id,host_name,query_type,True)
def find_tld(domain):
    #find the last occurence of a period which is the tld.....
    length = len(domain.split('.'))
    tld = domain.split('.')[len(domain.split('.')) - 1] #find the TLD of the domain name that was input
    if tld =='com':
        return 'com'
    elif tld =='org':
        return 'org'
    elif tld =='gov':
        return 'gov'
    else:
        return False #not a valid tld
def contact_root_server(vals,connection):
    #Start the root server....
    local_client = socket.socket()
    try:
        local_client.connect((localhost,5353)) #local client is the local client's agent to the root server....
        print("connected to the root server")
    except:
        print("Failed the connection")

    local_client.send(str(vals[1] + " " + str(vals[2])).encode()) #send the request to the root server

    root_client = socket.socket() #client for root...

    start_new_thread(root_server, (root_sock,root_client)) #start the root server....

    while True:
        root_response = local_client.recv(1024)
        print("Received from server: " + root_response.decode())

        if vals[2] == 'i': #if this is a iterative query.....

            local_client = socket.socket() #new client socket for the local server

            ip_addr = root_response.decode().split(':')[0] #ip address of the server
            port = int(root_response.decode().split(':')[1]) #port of the server...
            try:
                local_client.connect((localhost,port)) #local client is the local client's agent to the root server....
                print("connected to the tld server")
            except:
                print("Failed the connection")

            log_local("default_local," + str(vals[1]) + " , " + str(vals[2])) #Log the request........

            local_client.send(str(vals[1]).encode())

            while True:

                tld_response = local_client.recv(1024)

                cache[vals[1]] = tld_response.decode()

                print("Response Iterative from TLD Server: " + tld_response.decode())

                connection.send(tld_response)

                log_response(tld_response.decode() + "\n\n",vals[0]) #Log the response....

                break

        if vals[2] == 'r':
            connection.send(root_response)
            log_response(root_response.decode() + "\n\n",vals[0])

        break
def resolve_query(request,vals,connection): #resolves queries based on the query type.....
    if vals[2] == "i":
        print("Iterative Query")
        log_local("default_local, " + str(vals[1]) + "," + " I")
        contact_root_server(vals, connection)
    else:
        print("Recursive Query")
        log_local("default_local, " + str(vals[1]) + "," + " R")
        contact_root_server(vals,connection)

def new_query(connection): #this method takes in a connection to a client and listens for a query. Passes query to other methods to check user input validity.
    print("New Query....")
    while True: #Listen for queries
        data = connection.recv(1024)
        request = data.decode()

        if  not data:
            break

        print(request)

        vals = check_if_valid_query(request) #check user input to see if a valid request or a valid query.

        log_query(request, request.split(",")[0].lower())

        if vals == False:
            connection.send("0xEE, default_local, Invalid format".encode())
            log_response("0xEE, default_local, Invalid format\n\n", request.split(",")[0].lower())
        else:
            try: #Check the cache to see if already resolved....
                connection.send(cache[str(vals[1])].encode()) #send the hostname from the cache file....
                print("Sent From Cache")
                log_response("Sent from Cache: " + cache[str(vals[1])], vals[0])
            except:
                # Resolve the query....
                print("Query not Previously Resolved")
                log_local(request) #Log the invalid request in the default local file
                resolve_query(request,vals,connection)
    print("Broke out of the loop")

def sendShutdownAndWriteToCache(connections):
    for domain in cache: #cache each key in the cache
        print("Cached Domains: " + cache[domain] + "\n")
        cache_response(domain + "/" + cache[domain] + "\n")

    for conn in connections: #send shutdown message to all users
        conn.send("Connection has been closed by the server".encode())

def start_server(): # start the server and listen for connections...procceses new queries...
    connections = []
    atexit.register(sendShutdownAndWriteToCache,connections=connections) #this will run on sendShutdownAndWriteToCache() on shutdown
    while True:
        connection, addr = s.accept() #accept connections
        connections.append(connection) #add to list of connections to send shutdown message later on
        start_new_thread(new_query, (connection,)) #new thread for each connection
        print("Query Finished...") #the thread has run
    s.close()
    return None
def main():
    load_cache("cache.txt")
    start_server()
if __name__ == "__main__":
    main()
