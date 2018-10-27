# Server (Chat service - IT 347 - DGJNT) 

import sys
import socket
import select
import re
import traceback

#Switch statement implementation (source in lab writeup)
class switch(object):
    def __init__(self, value):
        self.value = value
        self.false = False
    def __iter__(self):
        yield self.match
        raise StopIteration
    def match(self, *args):
        if self.false or not args:
            return True
        elif re.match(args[0], self.value):
            self.false = True
            return True
        else:
            return False

#Defining lists and variables to be appended with data later on
host = "" 
port = 9020
receive_buffer = 4096 
conn_name = {}
buffer = []
socket_list = []

# Handle server connection
def server():
    # Libraries to start connection, avoid socket timeout, bind connection, and listen to 10 connections maximum
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, port))
    server_socket.listen(10)
 
    # Add server socket to list of connections
    socket_list.append(server_socket)
    
    #Server started message. We must stringify it since it is an integer
    print "Server started: " + str(port)
    
    # Loop during connection time--wait for inputs
    while True:
        #Get a list of sockets ready to be read
        ready_to_read, ready_to_write, in_error = select.select(socket_list, [], [], 0)

        for sock in ready_to_read:
            # Received a socket connection
            if sock == server_socket: 
                socket_forward, addr = server_socket.accept()
                socket_list.append(socket_forward)
                print "You have a new connection from IP %s, port %s" % addr
                socket_forward.send("Welcome to the DGJNT server! \r\n")
            else:
                # Handle commands received from client
                try:
                    # Receive data from socket
                    # Switch statement to handle inputs
                    data = sock.recv(receive_buffer)
                    if data:
                        for case in switch(data):
                            if case("help\r\n$"):
                                print "Received a help request"
                                sock.send(("Chat Server Help: "
                                           "\n'-> test: something' receives a response of 'something'"
                                           "\n'-> name: <chatname>' receives a response of 'OK'"
                                           "\n'-> get receives a response of the entire contents of the chat buffer."
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
                                conn_name[id(sock)] = data.replace('\r\n', '')[6:]
                                sock.send("OK\r\n")
                                break
                            if case("get\r\n$"):
                                print "Received a get request"
                                sock.send("\n".join(buffer) + "\r\n")
                                break
                            if case("push:\s[^\r\n]+\r\n$"):
                                print "Received a push request"
                                buffer.append("%s: %s" % ((conn_name[id(sock)] if id(sock) in conn_name else "unknown"), data[6:].replace('\r\n', '')))
                                sock.send("OK\r\n")
                                break
                            if case("getrange(\s\d+){2}\r\n$"):
                                print "Received a getrange request"
                                (start, end) = re.findall("\d+", data)
                                sock.send("\n".join(buffer[int(start): int(end) + 1]) + "\r\n" )
                                break
                            if case("adios\r\n$"):
                                print "Received an adios request"
                                sock.send("Goodbye!\n")
                                if id(sock) in conn_name:
                                    del conn_name[id(sock)]
                                sock.close()
                                if sock in socket_list:
                                    socket_list.remove(sock)
                                break
                            if case():
                                print "\n"
                                print data
                                sock.send("\n")
                                break
                    else:
                        # If the socket is not working, remove it   
                        if sock in socket_list:
                            socket_list.remove(sock)
                # Throw excetion if the data variable does not contain data from the buffer
                except Exception, err:
                    print traceback.format_exc()
                    print "Unexpected error:", sys.exc_info()[0]
                    continue
    #Close connection with socket
    server_socket.close()

if __name__ == "__main__":
    sys.exit(server())