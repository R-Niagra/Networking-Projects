import socket
import sys
import os
from thread import *
import shutil
import zipfile
import glob
import time


def makeSearchFile(addr):
	duplicates=0

	print "Came in with address: ",addr
	searchFile = open("search_content.txt", "w")
	recordFile=open("record.txt","a+")
	recordFile.seek(0)           #Brings cursor at start to readline!
	recordLines=recordFile.readlines()

	print" recordLines are",recordLines

	allTorrents = glob.glob("*.torrent")
	for torrent in allTorrents:
		with open(torrent) as f:
	   		lines = f.readlines()

		oneLine = lines[0].split(".")
		
		name=oneLine[0].split(":")

		# if not recordLines:
		# 	print "Got in"
		# 	recordFile.write(str(addr[0])+" "+str(addr[1])+" "+name[1]+"."+oneLine[1].rstrip()+" "+torrent+"\n")


		for line in recordLines:
			if torrent in line:
				duplicates+=1;		

		if(duplicates==0):
			recordFile.write(str(addr[0])+" "+str(addr[1])+" "+name[1]+"."+oneLine[1].rstrip()+" "+torrent+"\n")
			
		duplicates=0;


	   	lineToPrint = oneLine[0] + " type:" + oneLine[1].rstrip() + " tor:" + torrent + "\n"
	   	searchFile.write(lineToPrint)

	recordFile.close()
	searchFile.close()

	# print "record is: ",record
	# return record
	   	# print lineToPrint

def searchFile(reqFile,client):       #This will search and send appropriate torrent file
	searchFile=open("search_content.txt",'r')
	fileData=searchFile.readlines()
	
	divide=reqFile.split(".")
	name=divide[0]
	extension=divide[1]
	toFind="Name:"+name+ " type:"+extension
	
	for line in fileData:

		if toFind in line:
			print "rq line is: ",line
			reqTorrent=line.split("tor:",1)[1]
			reqTorrent=reqTorrent.strip()
			print"reqTorrent",reqTorrent
			with open(reqTorrent,'r') as inFile:
				torFile=inFile.readlines()
			client.send(''.join(torFile))
			client.recv(1024)

	
	time.sleep(.2)
	client.send("..Done Sending Torrents..")

	recordFile=open("record.txt",'r')
	record=recordFile.readlines()

	for line in record:
		if(reqFile in line):
			print line
			client.send(line)
			client.recv(1024)

	client.send("--ALL PEERS SENT--")
	print "Till this"
	recordFile.close()

	# 	print "Came in: "
	# 	print record[2]
	# 	if(record[2]==reqFile):
	# 		print "record:",record[0],record[1],record[2]




def clientThread(client,addr,count):

	while 1:

		print "Before"
		data = client.recv(1024)
		print "after"
		time.sleep(.3)
		print data

		if "~Download mode~" in data:

			reqFile=client.recv(2048)
			print reqFile
			searchFile(reqFile,client)
			# client.close()


		elif "~Sending Torrent File::~" in data:
			data=""
			with open('received_file%s.zip' %count, 'wb') as f:
				while True:
					data = client.recv(1024)
					f.write(data)
					# data = client.recv(1024)
					if "~^~Done Sending~^~" in data:
						break
					# data = client.recv(1024)
					

			client.send("Data received!")
			f.close()

			zip = zipfile.ZipFile('received_file%s.zip' %count)
			zip.extractall()
			makeSearchFile(addr)


		elif "^^Quiet^^" in data or not data:
			client.close()
			recordFile=open("record.txt","r")
			recordData=recordFile.readlines();
			recordFile.close();

			recordF=open("record.txt","w")
			for line in recordData:
				if addr[0]+" "+str(addr[1]) not in line:
					recordF.write(line)

			recordF.close()	
			return


		# if not data:
		# 	return

		data=""


def main(argv):

	# port = 1234                    # Reserve a port for your service.
	s = socket.socket()             # Create a socket object
	s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	host = '127.0.0.1'     				# Get local machine name
	s.bind((host,int(argv[1])))           # Bind to the port
	s.listen(5)                     # Now wait for client connection.
	# record=[[],[],[]]				#Record against Ip address,port, and file names
	count=1;


	while 1:
		client, addr = s.accept()     # Establish connection with client.
		start_new_thread(clientThread,(client,addr,count))
		print"In big while"
		count+=1
		# print "record in while is: ",record




if __name__=="__main__":
	main(sys.argv)
