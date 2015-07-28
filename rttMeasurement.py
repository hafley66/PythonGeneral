#!/usr/bin/env python
import os, sys, socket, struct, select, time, numpy as np, matplotlib.pyplot as plt
from citedCode import *
from customCode import Destination

# Prints the results of a destination objects best numbers.
def print_short_results(destObj):
    bestTTL = destObj.get_best_ttl
    bestRTT = destObj.get_best_rtt

### Implements the binary hop algorithm.
def get_hop_count(destObj) :
    
    left    = 0
    #initial TTL
    ttl     = 16
   
    #keep track if first maximum has been taken yet.
    left_taken  = 0
   
    while not (ttl - left) == 0 :
   
        #Send the ping
        rtt, icmp_type, code, packetID, sequence =  send_probe(destObj.destination, TTL=ttl)

        # Check the response
        if icmp_type is not None and icmp_type != -1:
            if      icmp_type == 0:

                # Save the result of the ping
                destObj.add_success(ttl, rtt)

                # Go half left
                ttl     = left + (ttl - left) / 2

                #The instant we hit a success, we know that it is either the best (lowest) TTL or is greater than the lowest one.
                #From now on we just go left and decrease our search by half each time until we have a change of 1 between ttl and left.
                left_taken = 1

            elif    icmp_type == 3 or icmp_type == 11 :
                
                # Save the result of the ping
                destObj.add_failure(ttl, rtt)

                if left_taken == 1:

                    # Go half right
                    prev    = ttl
                    ttl     += (ttl - left) / 2
                    left    = prev

                else :

                    # Go twice right (binary expansion)
                    left    = ttl
                    ttl     *= 2

            else:
                print "Unexpected TYPE := {0}, \n\t " \
                      "with CODE := {1}".format(icmp_type, code)

        elif icmp_type is None or icmp_type == -1:
            if icmp_type is None:
                print "\nDNS resolution failed"
            else :
                print "Timeout occured"
            print "{0}\n{0}\n\n".format("~" * (50 + len(" (HOPS, RTT) ")))
            return

    print_short_results(destObj)


# Prints the results of a destination objects best numbers.
def print_short_results(destObj):
    bestTTL = destObj.get_best_ttl
    bestRTT = destObj.get_best_rtt

    print "{0}{1}\t({2}, {3})\n{0}{0}\n".format("~" * (50 + len(" (HOPS, RTT) ")) + "\n",
                                               "~" * 25 + " (HOPS, RTT) " + "~" * 25 + "\n",
                                                bestTTL,
                                                bestRTT)

# Runs through each line of the targets.txt file and repeatedly pings the given site until it finds the lowest TTL that is successfull or has a timeout.
def main():
    f = open('targets.txt', 'r')
    i = 0
    # Prepare PLT
    plt.autoscale()
    
    for destination in f:

        # Text processing on the input.
        destination = str(destination.strip())
        
        # Create a new destination object. 
        destObj = Destination(destination)
        
        # Get the record of RTT vs TTl. The object passed in is changed by side effect. Return value not needed.
        get_hop_count(destObj)
        
        # Graph the results of the ping with the label of the current loop index.
        destObj.graph_with_plt(i)        
        
        # Increment loop variable
        i += 1

if __name__ == '__main__':
    main()