# Server (Chat service - IT 347 - DGJNT) 

import sys
import socket
import select
import re
import traceback

#Defining lists to be appended with data later on
HOST = "" 
PORT = 9020
SOCKET_LIST = []
RECV_BUFFER = 4096 
CHAT_BUFFER = []
CONNECTION_NAME = {}

#Switch statement implementation
class switch(object):
    def __init__(self, value):
        self.value = value
        self.fall = False
    def __iter__(self):
        yield self.match
        raise StopIteration
    
    def match(self, *args):
        if self.fall or not args:
            return True
        elif re.match(args[0], self.value):
            self.fall = True
            return True
        else:
            return False

#Function that handles server connection
def server():
    # Code to use socket package, avoid socket timeout, bind connection, and listen to connection
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(10)
 
    # Add server socket to list of connections
    SOCKET_LIST.append(server_socket)
 
    print "Server started on port: " + str(PORT)
    
    # Loop during connection time--wait for inputs
    while True:
        #Get a list of sockets ready to be read
        ready_to_read, ready_to_write, in_error = select.select(SOCKET_LIST, [], [], 0)

        for sock in ready_to_read:
            # Received a socket connection
            if sock == server_socket: 
                sockfd, addr = server_socket.accept()
                SOCKET_LIST.append(sockfd)
                print "Client (%s, %s) connected" % addr
                sockfd.send("Welcome to the DGJNT server! \r\n")
            else:
                # Handle commands received from client
                try:
                    # Receive data from socket
                    # Switch statement to handle inputs
                    data = sock.recv(RECV_BUFFER)
                    if data:
                        for case in switch(data):
                            if case("help\r\n$"):
                                print "Received a help request"
                                sock.send(("Chat Server Help: "
                                           "\n'-> test: something' receives a response of 'something'"
                                           "\n'-> name: <chatname>' receives a response of 'OK'"
                                           "\n'-> get receives a response of the entire contents of the chat buffer."
                                           "\n'-> guests receives a response of the all guests currently connected to server."
                                           "\n'-> push: <stuff>' receives a response of 'OK' The result is that '<chatname>: <stuff>' is added as a new line to the chat buffer."
                                           "\n'-> getrange <startline> <endline>' receives a response of lines <startline> through <endline> from the chat buffer. getrange assumes a 0-based buffer. Your client should return lines <startline> <endline-1>"
                                           "\n'-> adios' will quit the current connection.\r\n"))
                                break
                            if case("test:\s[^\r\n]+\r\n$"):
                                print "Received a test request"
                                sock.send(data[6:])
                                break
                            if case("name:\s[^\r\n]+\r\n$"):
                                print "Received a name request"
                                CONNECTION_NAME[id(sock)] = data.replace('\r\n', '')[6:]
                                sock.send("OK\r\n")
                                break
                            if case("get\r\n$"):
                                print "Received a get request"
                                sock.send("\n".join(CHAT_BUFFER) + "\r\n")
                                break
                            if case("guests\r\n$"):
                                print "Received a guest request"
                                users = len(CONNECTION_NAME)
                                guests = len(SOCKET_LIST) - (users + 1)
                                sock.send("%d Users\n" % (len(CONNECTION_NAME)) +
                                           (" * " if (users) else "") + 
                                           "\n * ".join(CONNECTION_NAME.values()) +
                                           ("\n" if (users) else "") + 
                                           "%d guests" % (len(SOCKET_LIST) - (len(CONNECTION_NAME) + 1)) +
                                           "\r\n")
                                break
                            if case("push:\s[^\r\n]+\r\n$"):
                                print "Received a push request"
                                CHAT_BUFFER.append("%s: %s" % ((CONNECTION_NAME[id(sock)] if id(sock) in CONNECTION_NAME else "unknown"), data[6:].replace('\r\n', '')))
                                sock.send("OK\r\n")
                                break
                            if case("getrange(\s\d+){2}\r\n$"):
                                print "Received a getrange request"
                                (start, end) = re.findall("\d+", data)
                                sock.send("\n".join(CHAT_BUFFER[int(start): int(end) + 1]) + "\r\n" )
                                break
                            if case("adios\r\n$"):
                                print "Received an adios request"
                                sock.send("Goodbye!\n")
                                if id(sock) in CONNECTION_NAME:
                                    del CONNECTION_NAME[id(sock)]
                                sock.close()
                                if sock in SOCKET_LIST:
                                    SOCKET_LIST.remove(sock)
                                break
                            if case():
                                print "\n"
                                print data
                                sock.send("\n")
                                break
                    else:
                        # If the socket is not working, remove it   
                        if sock in SOCKET_LIST:
                            SOCKET_LIST.remove(sock)
                # Throw excetion if the data variable does not contain data from the buffer
                except Exception, err:
                    print traceback.format_exc()
                    print "Unexpected error:", sys.exc_info()[0]
                    continue
    #Close connection with socket
    server_socket.close()

if __name__ == "__main__":
    sys.exit(server())