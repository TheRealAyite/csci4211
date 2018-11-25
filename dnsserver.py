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

#read the server.dat file......

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

        hostname = line[0].lower().replace(" ", "")
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

def log_local(message):
    file = open("default_local" + ".log", "a")
    file.write(message + "\n")
    file.close()

def com_server(socket):
    connection, addr = socket.accept()
    mapping = load_mapping('com')
    print(str(mapping) + " For com\n")
    while True:
        data = connection.recv(1024)
        request = data.decode()
        print("THIS IS THE REQUEST: " + request)
        if "www" not in request:
            request = "www." + request
        if  not data:
            break
        print("Received From Client (com): " + request + "\n")
        try:
            connection.send(mapping[request].encode()) #check the mapping and send the correct ip address to the requester.
            log_local("0x00, com, " + mapping[request] + "\n\n")
        except:
            print("0xFF, com, Host not found")
            #TODO....LOG IT
            log_local("0xFF, com, Host not found\n\n")
            connection.send("0xFF, com, Host not found".encode())
            print("Sent to the root server")
            break
    connection.close()
def gov_server(socket):
    connection, addr = socket.accept()
    mapping = load_mapping('gov')
    print(str(mapping) + " For gov\n")
    while True:
        data = connection.recv(1024)
        request = data.decode()
        print("THIS IS THE REQUEST: " + request)
        if "www" not in request:
            request = "www." + request
        if  not data:
            break
        print("Received From Client (gov): " + request + "\n")
        try:
            connection.send(mapping[request].encode())
            log_local("0x00, gov, " + mapping[request] + "\n\n") #check the mapping and send the correct ip address to the requester.
        except:
            print("0xFF, gov, Host not found")
            #TODO....LOG IT
            connection.send("0xFF, gov, Host not found".encode())
            log_local("0xFF, gov, Host not found\n\n")
            print("Sent to the root server")
            break
    print("Using print statements.")
    connection.close()
def org_server(socket):
    print("Org Socket Running....")
    connection, addr = socket.accept()
    print("Connection Accepted")
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
            log_local("0x00, org, " + mapping[request] + "\n\n") #check the mapping and send the correct ip address to the requester.

        except:
            print("0xFF, org, Host not found")
            #TODO....LOG IT
            connection.send("0xFF, org, Host not found".encode())
            print("Sent to the root server")
            log_local("0xFF, org, Host not found\n\n")
            break;

    connection.close()
def root_server(socket, client_socket):
    print("Waiting for connection....")
    connection, addr = socket.accept()
    localhost = '127.0.0.1'
    print("In Root Server....accepted conn")
    while True:
        data = connection.recv(1024)
        request = data.decode()
        print(request)
        print("Split: " + str(request.split(" ")))
        domain = request.split(" ")[0]
        query_type = request.split(" ")[1]
        print(domain)
        print("QUERY TYPE: " + query_type)
        print("This is the request: " + domain)

        if  not data:
            break
        if query_type == "r":
            #Rout to correct server.....gov com or org
            tld = find_tld(domain)
            if tld == 'org': #Contact the org_server....
                try:
                    client_socket.connect((localhost,5354))
                    print("Connected to the client socket")
                except OSError as ex:
                    print("Failed to connect to the client socket")
                    print(ex)
                client_socket.send(domain.encode()) #Send request to the org Server
                print("Sent request to org socket")
                while True:
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
                client_socket.send(domain.encode()) #Send request to the org Server
                print("Sent request to gov socket")
                while True:
                    response = client_socket.recv(1024).decode()
                    print("Recevied From TLD SERVER: " + response)
                    connection.send(response.encode())
                    print("Sent response to the local dns server....")
                    break
                print("Out of the loop. This is bad")
            elif tld == 'com':
                try:
                    client_socket.connect((localhost,5356))
                    print("Connected to the client socket")
                except OSError as ex:
                    print("Failed to connect to the client socket")
                    print(ex)
                client_socket.send(domain.encode()) #Send request to the org Server
                print("Sent request to com socket")
                while True:
                    response = client_socket.recv(1024).decode()
                    print("Recevied From TLD SERVER: " + response)
                    connection.send(response.encode())
                    print("Sent response to the local dns server....")
            else: #invalid TLD.....
                connection.send("0xEE, default_local, Invalid format".encode())
        else:
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
        print("Broke out of recv loop")
def check_if_valid_query(request):
    try: #split the query string into separate parameters to get the parameters of the DNS query.
        params = str(request).split(',')
        print(params)
    except:
        print("Invalid Format!!")
        return (False)
        sys.exit(1)
        #TODO: Loggingself.
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
        return (False)
    print(query_type)

    if query_type != "r" and query_type != "i":
        print("Invalid Query Type")
        log_query(response, client_id)
        log_error("0xEE, default_local, Invalid format",client_id)
        return (False)
    return (client_id,host_name,query_type,True)
def find_tld(domain):
    if 'org' in domain.split('.')[2]:
        return 'org'
    elif 'gov' in domain.split('.')[2]:
        return 'gov'
    elif 'com' in domain.split('.')[2]:
        return 'com'
    else:
        return False
def contact_root_server(vals,connection):
    #Start the root server....
    local_client = socket.socket()
    try:
        local_client.connect((localhost,5353)) #local client is the local client's agent to the root server....
        print("connected to the root server")
    except:
        print("Failed the connection")
    local_client.send(str(vals[1] + " " + str(vals[2])).encode())
    print("Sending....")
    while True:
        root_response = local_client.recv(1024)
        print("Received: " + root_response.decode())
        if vals[2] == 'i':
            local_client = socket.socket()
            ip_addr = root_response.decode().split(':')[0]
            port = int(root_response.decode().split(':')[1])
            print("IP addr: " + ip_addr)
            print("Port: " + str(port))
            try:
                local_client.connect((localhost,port)) #local client is the local client's agent to the root server....
                print("connected to the tld server")
            except:
                print("Failed the connection")
            log_local("default_local," + str(vals[1]) + " , " + str(vals[2])) #Log the request........
            local_client.send(str(vals[1]).encode())
            while True:
                tld_response = local_client.recv(1024)
                #TODO: Cache it..... & Log....
                print("Response Iterative from TLD Server: " + tld_response.decode())
                connection.send(tld_response)
                break
                #TODO: Cache it....\
        print("Hmmm......")
        connection.send(root_response)
        break
def resolve_query(request,vals,connection):
    if vals[2] == "i":
        print("Iterative Query")
        log_local("default_local, " + str(vals[1]) + "," + " I")
        contact_root_server(vals, connection)
    else:
        print("Recursive Query")
        log_local("default_local, " + str(vals[1]) + "," + " R")
        contact_root_server(vals,connection)

def new_query(connection):
    print("New Query....")
    while True: #Listen for queries
        data = connection.recv(1024)
        request = data.decode()
        if  not data:
            break
        print(request)
        vals = check_if_valid_query(request)
        print("VALS: " + str(vals))
        if vals == False:
            connection.send("0xEE, default_local, Invalid format".encode()) #TODO Change to OxEE
            sys.exit(1)
        try: #Check the cache to see if already resolved....
            connection.send(cache[str(vals[1])].encode()) #send the hostname from the cache file....
        except:
            # Resolve the query....
            print("Query not Previously Resolved")
            log_local(request) #Log the request in the default local file
            resolve_query(request,vals,connection)
def start_server():
    start_new_thread(root_server, (root_sock,root_client)) #start the root server....
    start_new_thread(org_server, (org_sock,)) #start the org server....
    start_new_thread(gov_server, (gov_sock,)) #start the gov server....
    start_new_thread(com_server, (com_sock,)) #start the com server....
    while True:
        print("In This Loop...Aceept")
        connection, addr = s.accept()
        start_new_thread(new_query, (connection,))
    s.close()
def main():
    load_cache("cache.txt")
    start_server()
if __name__ == "__main__":
    main()
