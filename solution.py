from socket import *
import os
import sys
import struct
import time
import select
import binascii
import statistics
# Should use stdev

ICMP_ECHO_REQUEST = 8
timeRTT = []
roundTrip_cnt =0
roundTrip_sum =0
roundTrip_min = 0
roundTrip_max =0
packageSent =0
timeARR= []



def checksum(string):
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



def receiveOnePing(mySocket, ID, timeout, destAddr):
    global roundTrip_min, roundTrip_max, roundTrip_sum, roundTrip_cnt, length, ttl
    timeLeft = timeout

    while 1:
        startedSelect = time.time()
        whatReady = select.select([mySocket], [], [], timeLeft)
        howLongInSelect = (time.time() - startedSelect)
        if whatReady[0] == []:  # Timeout
            return "Request timed out."

        timeReceived = time.time()
        recPacket, addr = mySocket.recvfrom(1024)

        # Fill in start
        type, code, checksum, id, seq = struct.unpack('bbHHh', recPacket[20:28])
        if ID == id:
            bytesInDouble = struct.calcsize('d')
            trans_time = struct.unpack('d', recPacket[28:28 + bytesInDouble])[0]
            #trans_time = struct.unpack('d', recPacket[28:])
            roundTrip = (timeReceived - trans_time) * 1000
            timeRTT.append(timeReceived - trans_time)
            #print ("time RTT", timeRTT)
            roundTrip_cnt += 1
            roundTrip_sum += roundTrip
            roundTrip_min = min(roundTrip_min, roundTrip)
            roundTrip_max = max(roundTrip_max, roundTrip)
            #timeRTT.append(timeReceived - timeData)
            ip_pkt_head = struct.unpack('!BBHHHBBH4s4s', recPacket[:20])
            ttl = ip_pkt_head[5]
            #saddr = socket.inet_ntoa(ip_pkt_head[8])
            length = len(recPacket) - 8
            return length, seq, ttl, roundTrip
        else:
            return "ID is not the same"


        # Fetch the ICMP header from the IP packet

        # Fill in end
        timeLeft = timeLeft - howLongInSelect
        if timeLeft <= 0:
            return "Request timed out."


def sendOnePing(mySocket, destAddr, ID):
    # Header is type (8), code (8), checksum (16), id (16), sequence (16)
    global packageSent
    myChecksum = 0
    # Make a dummy header with a 0 checksum
    # struct -- Interpret strings as packed binary data
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, 1)
    data = struct.pack("d", time.time())
    # Calculate the checksum on the data and the dummy header.
    myChecksum = checksum(header + data)

    # Get the right checksum, and put in the header

    if sys.platform == 'darwin':
        # Convert 16-bit integers from host to network  byte order
        myChecksum = htons(myChecksum) & 0xffff
    else:
        myChecksum = htons(myChecksum)


    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, 1)
    packet = header + data

    mySocket.sendto(packet, (destAddr, 1))
    packageSent += 1
    # AF_INET address must be tuple, not str


    # Both LISTS and TUPLES consist of a number of objects
    # which can be referenced by their position number within the object.

def doOnePing(destAddr, timeout):
    icmp = getprotobyname("icmp")


    # SOCK_RAW is a powerful socket type. For more details:   http://sockraw.org/papers/sock_raw
    mySocket = socket(AF_INET, SOCK_RAW, icmp)

    myID = os.getpid() & 0xFFFF  # Return the current process i
    sendOnePing(mySocket, destAddr, myID)
    delay = receiveOnePing(mySocket, myID, timeout, destAddr)
    mySocket.close()
    return delay


def ping(host, timeout=1):
    global dest
    # timeout=1 means: If one second goes by without a reply from the server,  	# the client assumes that either the client's ping or the server's pong is lost
    try:
        dest = gethostbyname(host)
    except socket.error as e:
        # raise socket.error(msg)
        print("Pinging " + host + " using Python:")
        print("")
        for i in range(0, 4):
            print("Request timed out.")
        print("")
        print("--- no.no.e ping statistics ---")
        print(roundTrip_sum, " packets transmitted, 0 packets received, 100% packet loss")
        print("round-trip min/avg/max/stddev = 0/0.0/0.0/0.0 ms")
        exit()
    print("Pinging " + dest + " using Python:")
    print("")


    # Calculate vars values and return them
    #  vars = [str(round(packet_min, 2)), str(round(packet_avg, 2)), str(round(packet_max, 2)),str(round(stdev(stdev_var), 2))]
    # Send ping requests to a server separated by approximately one second
    for i in range(0,4):
        delay = doOnePing(dest, timeout)
        overall_time = round(timeRTT[i]*1000, 7)
        timeARR.append(overall_time)
        #print ("time RTT", timeRTT)
        print("Reply from " + dest + ": bytes=" + str(length) + " time=" + str(overall_time) + "ms" + " TTL=" + str(ttl))
        time.sleep(1)  # one second
    print("")
    packet_stdev = round(statistics.stdev(timeARR), 2)
    print("---", host, "ping statistics ---")
    print(str(packageSent) + " packets transmitted, " + str(roundTrip_cnt) + " packets received, " + str(100 * (
            (packageSent - roundTrip_cnt) / packageSent) if roundTrip_sum > 0 else 0) + "% packet loss")
    packet_min = (min(timeRTT) if len(timeRTT) > 0 else 0)
    packet_avg = float(sum(timeRTT) / len(timeRTT)
                       if len(timeRTT) > 0 else float("nan"))
    #print ("sum(timeRTT)", sum(timeRTT), "lentime RTT", len(timeRTT))
    packet_max = (max(timeRTT) if len(timeRTT) > 0 else 0)
    print("round-trip min/avg/max/stddev = " + str(round(packet_min * 1000, 2)) + "/" + str(
        round(packet_avg, 2)) + "/" + str(round(packet_max * 1000, 2)) + "/" + str(packet_stdev) + " ms")
    #vars = [str(round(packet_min, 2)), str(round(packet_avg, 2)), str(round(packet_max, 2)),str(round(packet_stdev))]
    #print ("vars",vars)

        #print(delay)
        #time.sleep(1)  # one second

    return vars

if __name__ == '__main__':
    ping("google.co.il")
