# Client (Chat service - IT 347 - DGJNT) 

import socket
import select 
import sys 

def client():

    # Get the parameters the user inputs
    host = str(sys.argv[1]) 
    port = int(sys.argv[2])

    # Server connection
    server_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 

    # Connect to the server
    try:
        server_connection.connect((host, port))
    except:
        print("Connection failed.")
        sys.exit()

    print("Connection established.")
    
    # Prompt for a name, and use that name in the chat
    name = raw_input("What is your name: ")
 
    # Clean buffer
    sys.stdout.flush()

    while True: 
        # List containing inputs
        sockets_list = [sys.stdin, server_connection] 

        # List of readable, writeable, and error sockets
        read_sockets, write_socket, error_socket = select.select(sockets_list, [], []) 

        for socks in read_sockets: 
            if socks == server_connection: 
                # Receive message from server acknoledging connection, exit if none
                message = socks.recv(4046)
                if not message:
                    sys.exit()
                else:
                    sys.stdout.write(message)
                    sys.stdout.write(name + "-> "); sys.stdout.flush()
            else: 
                message = sys.stdin.readline().replace('\n', '\r\n') 
                server_connection.send(message) 
                sys.stdout.flush() 
    server_connection.close()

if __name__ == "__main__":
    sys.exit(client()) 
