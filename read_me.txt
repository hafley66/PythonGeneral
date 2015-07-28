Run as specified per the instructions.
Target sites are already named and ready for processing by the script. 
I used matplotlib.pyplot to graph the results and save them as 'png' image files.  


1. You can tell if the TTL is too small if an ICMP response is returned with code 3 (didn't reach) or 11 (TTL expired).
	
	You can tell if the TTL is too big if you get a successful response back. This is ICMP type 0 (echo response).

	To find the right TTL, binary search until you increase/decrease the TTL by one. Then find which of those two adjacent TTL's was successful, and that is the approximate hop distance to the destination.

2. The ICMP messages are matched by setting the process id on the host machine as the id for the ICMP packet. 

	I place this matching information in the header of the ICMP packet.

3. Reasons for no answer : 
	a) Timeout
	b) TTL was too short
	c) Use of UDP makes the transport of the packet unreliable at the transport layer. 