from socket import *


def smtp_client(port=1025, mailserver='127.0.0.1'):
    msg = "\r\n My message"
    endmsg = "\r\n.\r\n"
    mserver = (mailserver,port)

    # Choose a mail server (e.g. Google mail server) if you want to verify the script beyond GradeScope

    # Create socket called clientSocket and establish a TCP connection with mailserver and port

    # Fill in start
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect(mserver)
    # Fill in end

    recv = clientSocket.recv(1024).decode()
    #print("Message after connection request:" + recv)
    #if recv[:3] != '220':
     #   print('220 reply not received from server.')

    # Send HELO command and print server response.
    heloCommand = 'EHLO Alice\r\n'
    clientSocket.send(heloCommand.encode())
    recv1 = clientSocket.recv(1024).decode()
    #print("Message for HELO command:"+ recv1)
    #if recv1[:3] != '250':
     #   print('250 reply not received from server.')




if __name__ == '__main__':
    smtp_client(1025, '127.0.0.1')

