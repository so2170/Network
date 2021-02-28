from socket import *
import os
import sys
import struct
import time
import select
import math
import statistics
import binascii
# Should use stdev

ICMP_ECHO_REQUEST = 8
#timeRTT = []
timeRTT =[]
packageSent =0
packageRev = 0
packet_min =0
packet_max =0
packet_avg=0


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
   global packageRev,timeRTT,packet_min,packet_max,packet_avg
   timeLeft = timeout

   global received
   global roundTripTimeLog
   timeRemaining = timeout
   while 1:
       startedSelect = time.time()
       # print ("Startedtime:",startedSelect)
       whatReady = select.select([mySocket], [], [], timeLeft)
       # print("time.time:",time.time())
       howLongInSelect = (time.time() - startedSelect)
       # print ("howlonginseelct:", howLongInSelect)
       if whatReady[0] == []:  # Timeout
           return "Request timed out."

       timeReceived = time.time()
       # print ("timereceived:", timeReceived)
       recPacket, addr = mySocket.recvfrom(1024)
       # print ("recPacket:", recPacket, "Addr:", addr)
       # Fill in start
       icmpHeader = recPacket[20:28]
       icmpType, code, mychecksum, packetID, sequence = struct.unpack("bbHHh", icmpHeader)
       # print("the header received:"+ icmpType, code, mychecksum, packetID, str(sequence))
       if packetID == ID:
           bytesInDouble = struct.calcsize("d")
           timeSent = struct.unpack("d", recPacket[28:28 + bytesInDouble])[0]
           #print("timesent", timeSent)

           # print ("timeRTT:", timeRTT)
           # print("timesent:"+timeSent)
           diff = timeReceived - timeSent
           timeRTT.append(diff)
           packageRev += 1
           #print("timeRTT:", timeRTT)
           # mean = statistics.mean(timeRTT)
           # print("mean:",mean)
           # print("timeRTT lenght:", len(timeRTT))
           # print("timeRTT min", min(timeRTT))
           # print("timeRTT max", max(timeRTT))
           #print("timeRTT avg", float(sum(timeRTT)/len((timeRTT))))
           # print("timeRTT stdev" %(statistics.stdev(timeRTT,xbar=mean)))
           # print("timeRTT stdev", float(math.sqrt(sum(timeRTT)/len(timeRTT) - sum(timeRTT/len(timeRTT)**2))) )
           #packet_min = min(timeRTT) if len(timeRTT) > 0 else 0
           #packet_max = max(timeRTT) if len(timeRTT) > 0 else 0
           #timeRTT_sum = sum(timeRTT)
           #print ("timeRTTsum",timeRTT_sum)
           # print("sum timertt", sum(timeRTT), "len time rtt", len(timeRTT))
           #print("packageREv", packageRev)
           #packet_avg=(timeRTT_sum / packageRev)
           #print("printAVg:", packet_avg)
           #mean = statistics.mean(timeRTT)
           #under_root = ((sum(timeRTT)-mean)**2)*1.0/packageRev
           #print ("standard deviation",math.sqrt(under_root))


           # print(
           #   "maxRTT:", (max(timeRTT) if len(timeRTT) > 0 else 0), "\tminRTT:", (
           #      min(timeRTT) if len(timeRTT) > 0 else 0), "\naverageRTT:", float(
           #     sum(timeRTT) / len(timeRTT) if len(timeRTT) > 0 else float("nan")))

           return diff
       else:
           return "0: IP Header bad"

       # Fetch the ICMP header from the IP packet

       # Fill in end
       timeLeft = timeLeft - howLongInSelect
       if timeLeft <= 0:
           return "Request timed out."


def sendOnePing(mySocket, destAddr, ID):
   # Header is type (8), code (8), checksum (16), id (16), sequence (16)

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

   mySocket.sendto(packet, (destAddr, 1))  # AF_INET address must be tuple, not str


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
   # timeout=1 means: If one second goes by without a reply from the server,      # the client assumes that either the client's ping or the server's pong is lost
   dest = gethostbyname(host)
   #print("Pinging " + dest + " using Python:")
   #print("")
   # Calculate vars values and return them

   #if len(timeRTT)>0:
    #   packet_min = min(timeRTT)
   #else:
    #   packet_min = 0

   #vars = [str(round(packet_min, 2)), str(round(packet_avg, 2)), str(round(packet_max, 2)),str(round(stdev(stdev_var), 2))]
   # Send ping requests to a server separated by approximately one second
   for i in range(0,4):
       delay = doOnePing(dest, timeout)

      # print ("MaxRTT:",(max(timeRTT) if len(timeRTT)>0 else 0))
       #vars = [float(round(packet_min, 2)), float(round(packet_avg, 2)), float(round(packet_max, 2))]
       #print("vars:", vars)

       time.sleep(1)  # one second
   #print("packet_min",str(round(packet_min,2)))
   #print("packet_max", str(round(packet_max, 2)))
   #print("timeRTT:", timeRTT, "sum of timeRTT:", sum(timeRTT))
   packet_min = min(timeRTT) if len(timeRTT) > 0 else 0
   packet_max = max(timeRTT) if len(timeRTT) > 0 else 0
   packet_avg = (sum(timeRTT) / packageRev)
   mean = statistics.mean(timeRTT)
   under_root = ((sum(timeRTT) - mean) ** 2) * 1.0 / packageRev
   # print ("standard deviation",math.sqrt(under_root))
   stdev_var = math.sqrt(under_root)
   vars = [float(round(packet_min, 2)),float(round(packet_avg,2)), float(round(packet_max, 2)), float(round(stdev_var,2))]
   #print(vars)
   return vars

if __name__ == '__main__':
   ping("google.co.il")
   #ping("173.12.11.12")


