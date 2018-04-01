import socket
import sys
import os.path
import time
from thread import *


def main(argv):
	sock=socket.socket(socket.AF_INET,socket.SOCK_DGRAM) 
	sip=argv[1]
	sport=int(argv[2])
	addr=(sip,sport)
	sock.setblocking(0)

	query=raw_input("Plese enter your Query:- ")
	sock.sendto("15440,-,-1,-,-,%s,-" %query ,addr)
	pingTime=time.time()+5	

	while True:
		
		# data,addr=sock.recvfrom(1024)	

		try:

			data,addr=sock.recvfrom(1024)

		except socket.error as error:

			if "[Errno 35]" in str(error):
				# if(time.time()>=ping):
				# 	sock.sendto("15440,-,3,-,-,-,-",addr) 
				if(time.time()>pingTime):        #Pings every 5 seconds
					print "Pinging"
					sock.sendto("15440,-,0,-,-,-,-",addr)
					pingTime=time.time()+5

				continue

			else:
				raise error


		print data
			



if __name__=="__main__":
	main(sys.argv)