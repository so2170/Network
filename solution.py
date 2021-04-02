from socket import *
import os
import sys
import struct
import time
import select
import socket
import binascii


ICMP_ECHO_REQUEST = 8
#MAX_HOPS = 30
MAX_HOPS = 30
TIMEOUT = 2.0
TRIES = 1
flag = 0
a = ''
b = ''
c = ''
d = ''
e = ''
f = ''
g = ''
# The packet that we shall send to each router along the path is the ICMP echo
# request packet, which is exactly what we had used in the ICMP ping exercise.
# We shall use the same packet that we built in the Ping exercise


def checksum(string):
# In this function we make the checksum of our packet
    csum = 0
    countTo = (len(string) // 2) * 2
    count = 0


    while count < countTo:
        thisVal = (string[count + 1]) * 256 + (string[count])
        csum += thisVal
        csum &= 0xffffffff
        count += 2


    if countTo < len(string):
        csum += (string[len(string) - 1])
        csum &= 0xffffffff


    csum = (csum >> 16) + (csum & 0xffff)
    csum = csum + (csum >> 16)
    answer = ~csum
    answer = answer & 0xffff
    answer = answer >> 8 | (answer << 8 & 0xff00)
    return answer


def build_packet():
    #Fill in start
    # In the sendOnePing() method of the ICMP Ping exercise ,firstly the header of our
    # packet to be sent was made, secondly the checksum was appended to the header and
    # then finally the complete packet was sent to the destination.


    # Make the header in a similar way to the ping exercise.
    myChecksum = 0
    myID = os.getpid() & 0xFFFF
    #print(myID)

    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, myID, 1)
    data = struct.pack("d", time.time())
    # Append checksum to the header.
    myChecksum = checksum(header + data)
    if sys.platform == 'darwin':
        myChecksum = socket.htons(myChecksum) & 0xffff
        # Convert 16-bit integers from host to network byte order.
    else:
        myChecksum = htons(myChecksum)

    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, myID, 1)
    # Don’t send the packet yet , just return the final packet in this function.
    #Fill in end


    # So the function ending should look like this


    packet = header + data
    return packet


def get_route(hostname):
    timeLeft = TIMEOUT
    global flag
    tracelist1 = [] #This is your list to use when iterating through each trace
    tracelist2 = [] #This is your list to contain all traces


    for ttl in range(1,MAX_HOPS):
        for tries in range(TRIES):
            destAddr = gethostbyname(hostname)


            #Fill in start
            icmp=socket.getprotobyname("icmp")
            mySocket = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)
            # Make a raw socket named mySocket
            #Fill in end


            mySocket.setsockopt(IPPROTO_IP, IP_TTL, struct.pack('I', ttl))
            mySocket.settimeout(TIMEOUT)
            try:
                d = build_packet()
                mySocket.sendto(d, (hostname, 0))
                t= time.time()
                startedSelect = time.time()
                whatReady = select.select([mySocket], [], [], timeLeft)
                howLongInSelect = (time.time() - startedSelect)
                if whatReady[0] == []: # Timeout
                    flag += 1
                    b=(str(ttl) + "," + "*" + "," + "Request timed out")

                    tracelist1.append(b.split(","))

                    #print(b)
                    #Fill in start
                    #You should add the list above to your all traces list
                    #Fill in end

                recvPacket, addr = mySocket.recvfrom(1024)
                curraddr = addr[0]
                curr_name = str(socket.getfqdn(curraddr))

                try:
                    if curr_name == addr[0]:
                        h = "hostname not returnable"
                        # print (h)
                    else:
                        curr_name != addr[0]
                        h = curr_name
                except socket.error:
                    pass

                timeReceived = time.time()
                timeLeft = timeLeft - howLongInSelect
                if timeLeft <= 0:
                    flag += 1
                    c=(str(ttl) + "," + "*" + "," + "Request timed out")
                    tracelist1.append(c.split(","))
                    #print(c)
                    #You should add the list above to your all traces list
                    #Fill in end
            except timeout:
                continue


            else:
                #Fill in start
                icmpHeader = recvPacket[20:28]
                types, code, checksum, packetID, sequence = struct.unpack("bbHHh", icmpHeader)
                #Fill in end
                #try:
                 #   print("abc")
                    #Fill in start
                    #Fill in start

                    #Fill in end
                #except error:   #if the host does not provide a hostname
                    #Fill in start
                    #Fill in end


                if types == 11:
                    bytes = struct.calcsize("d")
                    timeSent = struct.unpack("d", recvPacket[28:28 + bytes])[0]
                    #Fill in start
                    #You should add your responses to your lists here
                    flag +=1
                    e=(str(ttl) + "," + str(round((timeReceived - t) * 1000)) + "ms" + ","+ str(addr[0]) + "," + h)
                    tracelist1.append(e.split(","))
                    #print(e)
                    #Fill in end
                elif types == 3:
                    bytes = struct.calcsize("d")
                    timeSent = struct.unpack("d", recvPacket[28:28 + bytes])[0]
                    #Fill in start
                    #You should add your responses to your lists here
                    flag +=1
                    d=(str(ttl) + "," + str(round((timeReceived - t) * 1000)) +"ms"+ "," + str(addr[0]) + "," + h)
                    tracelist1.append(d.split(","))
                    #print(d)
                    #Fill in end
                elif types == 0:
                    bytes = struct.calcsize("d")
                    timeSent = struct.unpack("d", recvPacket[28:28 + bytes])[0]
                    #Fill in start
                    e=str(ttl) + "," + str(round((timeReceived - timeSent) * 1000)) +"ms" + "," + str(addr[0]) + "," + hostname
                    tracelist1.append(e.split(","))
                    #print(e)
                    tracelist2.append(tracelist1)
                    #print(destAddr)
                    #print(tracelist1)
                    return tracelist1
                    #You should add your responses to your lists here and return your list if your destination IP is met
                    #Fill in end
                else:
                    tracelist1.append("error")
                    tracelist2.append(tracelist1)
                    #Fill in start
                    #If there is an exception/error to your if statements, you should append that to your list here
                    #Fill in end
                break
            finally:
                mySocket.close()

if __name__ == '__main__':
    get_route("www.bing.com")
