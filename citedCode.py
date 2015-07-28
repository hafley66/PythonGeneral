#!/usr/bin/env python


"""
    A pure python ping implementation using raw socket.


    Note that ICMP messages can only be sent from processes running as root.

    Derived from ping.c distributed in Linux's netkit. That code is
    copyright (c) 1989 by The Regents of the University of California.
    That code is in turn derived from code written by Mike Muuss of the
    US Army Ballistic Research Laboratory in December, 1983 and
    placed in the public domain. They have my thanks.

    Bugs are naturally mine. I'd be glad to hear about them. There are
    certainly word - size dependenceies here.

    Copyright (c) Matthew Dixon Cowles, <http://www.visi.com/~mdc/>.
    Distributable under the terms of the GNU General Public License
    version 2. Provided with no warranties of any sort.

    Original Version from Matthew Dixon Cowles:
      -> ftp://ftp.visi.com/users/mdc/ping.py

    Rewrite by Jens Diemer:
      -> http://www.python-forum.de/post-69122.html#69122

    Rewrite by George Notaras:
      -> http://www.g-loaded.eu/2009/10/30/python-ping/
"""


import os, sys, socket, struct, select, time, numpy as np, matplotlib.pyplot as plt

# From /usr/include/linux/icmp.h; your milage may vary.
ICMP_ECHO_REQUEST   = 8 # Seems to be the same on Solaris.
unlikelyPort        = 45555

### This is not my code, this is the code from the authors introduced above.
def checksum(source_string):
    sum = 0
    countTo = (len(source_string)/2)*2
    count = 0
    while count<countTo:
        thisVal = ord(source_string[count + 1])*256 + ord(source_string[count])
        sum = sum + thisVal
        sum = sum & 0xffffffff # Necessary?
        count = count + 2

    if countTo<len(source_string):
        sum = sum + ord(source_string[len(source_string) - 1])
        sum = sum & 0xffffffff # Necessary?

    sum = (sum >> 16)  +  (sum & 0xffff)
    sum = sum + (sum >> 16)
    answer = ~sum
    answer = answer & 0xffff

    # Swap bytes. Bugger me if I know why.
    answer = answer >> 8 | (answer << 8 & 0xff00)

    return answer


### Modified code from authors above. Will indicate who wrote what. 
### I have refitted the majority of this code. All that is really left over is the select call and 
### decoding the header message. 
def receive_one_ping(my_socket, ID, timeout):
    """
    receive the ping from the socket.
    """
    timeLeft = timeout
    while True:
        startedSelect = time.time()
        whatReady = select.select([my_socket], [], [], 2)

        if whatReady[0] == []: # Timeout
            return 0, -1, -1, -1, -1

        timeReceived = time.time()

        ### These three lines are not my code. Authors above.
        recPacket, addr = my_socket.recvfrom(1024)
        icmpHeader = recPacket[20:28]
        type, code, checksum, packetID, sequence = struct.unpack(
            "bbHHh", icmpHeader
        )
        print "*" * 10 + "RECEIVED" + "*"*10 + "\n\t"\
              "TYPE         = {0}, \n\t" \
              "PACKET_ID    = {1}, \n\t" \
              "CODE         = {2}, \n\t" \
              "RTT          = {3}".format(type, packetID, code, timeReceived - startedSelect)


        print "-" * 50 + "\n"
        
        if packetID == ID:
            bytesInDouble = struct.calcsize("d")
            timeSent = struct.unpack("d", recPacket[28:28 + bytesInDouble])[0]
            return timeReceived - timeSent, type, code, packetID, sequence
        else:
            return timeReceived - startedSelect, type, code, packetID, sequence

### Code from the authors above
def send_one_ping(my_socket, dest, ICMP_REQUEST_TYPE=ICMP_ECHO_REQUEST, code=0,ID=1, TTL=1):
    """
    Send one ping to the given >dest_addr<.
    """
    print "SENDING TO\n" +  str(dest) + "\nWITH TTL = " + str(TTL)

    try:
        dest_addr  =  socket.gethostbyname(dest)
    except socket.gaierror, (err, msg):
        print socket.error(msg)
        return 0
    # Header is type (8), code (8), checksum (16), id (16), sequence (16)
    my_checksum = 0

    # Make a dummy heder with a 0 checksum.
    header = struct.pack("bbHHh", ICMP_REQUEST_TYPE, code, my_checksum, ID, 1)
    bytesInDouble = struct.calcsize("d")
    data = (192 - bytesInDouble) * "Q"
    data = struct.pack("d", time.time()) + data

    # Calculate the checksum on the data and the dummy header.
    my_checksum = checksum(header + data)

    # Now that we have the right checksum, we put that in. It's just easier
    # to make up a new header than to stuff it into the dummy.
    header = struct.pack(
        "bbHHh", ICMP_REQUEST_TYPE, 0, socket.htons(my_checksum), ID, 1
    )
    print "\t" \
          "ICMP_REQUEST_TYPE    : {0},\n\t" \
          "CODE                 : {1},\n\t" \
          "ID                   : {2},\n\t" \
          "TTL                  : {3}".format(ICMP_REQUEST_TYPE, code, ID, TTL)
    packet = header + data

    ### Set time to live before sending the packet. 
    my_socket.setsockopt(socket.SOL_IP, socket.IP_TTL, TTL)
    my_socket.sendto(packet, (dest_addr, 1))
    return 1

####Code refitted from authors.
def send_probe(dest_addr, timeout = 10000, TTL=16):
    """
    Returns either the delay (in seconds) or none on timeout.
    """
    icmp = socket.getprotobyname("icmp")
    try:
        my_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)
    except socket.error, (errno, msg):
        if errno == 1:
            # Operation not permitted
            msg = msg + (
                " - Note that ICMP messages can only be sent from processes"
                " running as root."
            )
            raise socket.error(msg)
        raise # raise the original error

    ### Help identify packets by using process id on computer.
    my_ID = os.getpid() & 0xFFFF


    [delay, icmp_type, code, packetID, sequence] = [-1, None, -1, -1, -1]
    if send_one_ping(my_socket, dest_addr, ID=my_ID, TTL=TTL) :
        delay, icmp_type, code, packetID, sequence = receive_one_ping(my_socket, my_ID, timeout)
    my_socket.close()
    return delay, icmp_type, code, packetID, sequence
