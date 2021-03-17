from socket import *
import os
import sys
import struct
import time
import select
import binascii
import socket
import statistics

ICMP_ECHO_REQUEST = 8
timeRTT = []
packageSent = 0
packageRev = 0
ttl = 0
data_len = 0
timeArr = []
dest = 0
stdev_vars=[]


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
    global packageRev, timeRTT, ttl, ip_pkt_head, data_len
    timeLeft = timeout
    while 1:
        startedSelect = time.time()
        whatReady = select.select([mySocket], [], [], timeLeft)
        howLongInSelect = (time.time() - startedSelect)
        if whatReady[0] == []:  # Timeout
            return "Request timed out."
        timeReceived = time.time()
        recPacket, addr = mySocket.recvfrom(1024)
        #print (len(recPacket))

        # Fill in start
        # Fetch the ICMP header from the IP packet
        icmpHeader = recPacket[20:28]
        #print (icmpHeader)
        requestType, code, revChecksum, revId, revSequence = struct.unpack(
            'bbHHh', icmpHeader)
        if ID == revId:
            bytesInDouble = struct.calcsize('d')
            timeData = struct.unpack('d', recPacket[28:28 + bytesInDouble])[0]
            timeRTT.append(timeReceived - timeData)
            packageRev += 1
            ip_pkt_head = struct.unpack('!BBHHHBBHII', recPacket[:20])
            #print(ip_pkt_head)
            ttl = ip_pkt_head[5]
            #print(ip_pkt_head[2])
            data_len = len(recPacket)
           # print ("time recevied - time data", timeReceived-timeData , " ttl", ttl,"data_len", data_len)
            return timeReceived - timeData
        else:
            return "ID is not the same!"

        # Fill in end
        timeLeft = timeLeft - howLongInSelect
        if timeLeft <= 0:
            return "Request timed out."


def sendOnePing(mySocket, destAddr, ID):
    global packageSent
    # Header is type (8), code (8), checksum (16), id (16), sequence (16)
    myChecksum = 0
    # Make a dummy header with a 0 checksum.
    # struct -- Interpret strings as packed binary data
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, 1)
    data = struct.pack("d", time.time())
    # Calculate the checksum on the data and the dummy header.
    myChecksum = checksum(header + data)
    # Get the right checksum, and put in the header
    if sys.platform == 'darwin':
        myChecksum = socket.htons(myChecksum) & 0xffff
        # Convert 16-bit integers from host to network byte order.
    else:
        myChecksum = socket.htons(myChecksum)
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, 1)
    packet = header + data
    mySocket.sendto(packet, (destAddr, 1))
    packageSent += 1

    # AF_INET address must be tuple, not str
    # Both LISTS and TUPLES consist of a number of objects
    # which can be referenced by their position number within the object


def doOnePing(destAddr, timeout):
    icmp = getprotobyname("icmp")
    # SOCK_RAW is a powerful socket type. For more details see:http://sock-raw.org/papers/sock_raw
    try:
        mySocket = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)
    except socket.error as e:
        if e.errno == 1:
            raise socket.error("error")

    # Fill in end
    myID = os.getpid() & 0xFFFF  # Return the current process i
    sendOnePing(mySocket, destAddr, myID)
    delay = receiveOnePing(mySocket, myID, timeout, destAddr)
    mySocket.close()
    return delay


def ping(host, timeout=1):
    global dest, stdev_vars
    # timeout=1 means: If one second goes by without a reply from the server,
    try:
        dest = gethostbyname(host)

    except socket.error as e:
        # raise socket.error(msg)
        #print("Pinging " + host + " using Python:")
        #print("")
        #for i in range(0, 4):
        #    print("Request timed out.")
        #print("")
        #print("--- no.no.e ping statistics ---")
        #print(packageSent, " packets transmitted, 0 packets received, 100% packet loss")
        #print("round-trip min/avg/max/stddev = 0/0.0/0.0/0.0 ms")
        exit()
    #print("Pinging " + dest + " using Python:")
    #print("")
    # vars = [str(round(packet_min, 2)), str(round(packet_avg, 2)), str(
    # round(packet_max, 2)), str(round(stdev(stdev_var), 2))]
    # Send ping requests to a server separated by approximately one second
    for i in range(0, 4):
        delay = doOnePing(dest, timeout)
        stdev_vars.append(delay *1000)
        #print ("delay",delay)
        #overall_time = round(timeRTT[i] * 1000, 7)
        #timeArr.append(overall_time)
        #print("Reply from " + dest + ": bytes=" + str(data_len) + " time=" + str(round(delay * 1000, 2)) + "ms" + " TTL=" + str(ttl))
        time.sleep(1)  # one second
    #print("")
    packet_stdev = round(statistics.stdev(stdev_vars), 2)
    #print("---", host, "ping statistics ---")
    #print(str(packageSent) + " packets transmitted, " + str(packageRev) + " packets received, " + str(100 * ((packageSent - packageRev) / packageSent) if packageRev > 0 else 0) + "% packet loss")
    packet_min = (min(timeRTT) if len(timeRTT) > 0 else 0)
    packet_avg = float(sum(timeRTT) / len(timeRTT)
                       if len(timeRTT) > 0 else float("nan"))
    packet_max = (max(timeRTT) if len(timeRTT) > 0 else 0)
    #print("round-trip min/avg/max/stddev = " + str(round(packet_min * 1000, 2)) + "/" + str(round(packet_avg * 1000, 2)) + "/" + str(round(packet_max * 1000, 2)) + "/" + str(packet_stdev) + " ms")
    vars = [str(round(packet_min*1000, 2)), str(round(packet_avg*1000, 2)), str(round(packet_max*1000, 2)),str(packet_stdev)]
    #print(vars)
    return vars

if __name__ == '__main__':
    ping("google.co.il")
    #ping("192.0.0.1")
