#AUTHOR:
    #Ayite D'almeida,
    #X500: dalme003@umn.edu
    #Queries a local DNS server for domain names based on the ID,host_name,query_type format.
    
import socket
from _thread import *
from time import sleep

def listen(socket): #Create a thread to listen for requests. This is for the shutdown message mostly but listenes for all responses from local server
    while True:
        data = socket.recv(2048) #receive
        response = data.decode() #string processing
        if  not data:
            break
        print(response + "\n") #print
def start_client():
    host = '127.0.0.1'
    port = 5352 #this is location of the local server

    s = socket.socket() #Create a new socket for sending requests
    s.connect((host, port)) #Connect to the local server

    message = input("Please enter you query. (CLIENT ID, HOSTNAME, I/R) separate the parameters by comma. No need for parens: ") #accept input
    while message != 'q':
        s.send(message.encode()) #send the data to the local server....
        while True:
            start_new_thread(listen, (s,)) #Start a new thread and listen
            sleep(1) #Sleep the thread so print statements print in order...
            break  # if thread ran sucefully we know we got a response...
        message = input("Please Enter A Query: ")
    s.close() #close the connection on quit.



if __name__ == "__main__":
    start_client()
