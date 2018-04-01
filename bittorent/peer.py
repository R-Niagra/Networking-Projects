from __future__ import division
from collections import Counter
import math
import socket
import sys
import os.path
from thread import *
import shutil
import uuid
import random
import time


def createTorrents(uploadsPath, torrentsPath):

	count = random.randint(0,100)
	count=count^2+31
	print "count: ",count 
	if not os.path.exists(torrentsPath):
		os.makedirs(torrentsPath)
	
	files = os.listdir(uploadsPath)
	print files
	for file in files:
		count = count + 1
		torrent = open(("torrents/" + str(count) + ".torrent"), "w")
		torrent.write("Name:%s\n" %file)
		torrent.write("Key : " + str(uuid.uuid4()) + "\n")
		torrent.write("size : %d bytes\n" %os.path.getsize(uploadsPath+"/"+file))
		torrent.write("n_parts : 30\n")

# def breakConnection(s)
# 	s.close()

def sendToPeer(client,addr):
	client.send("U are connected with the peer!!!!!!!!!!")
	file2Send=client.recv(1024)

	downloadRecord=open("downloadRecord.txt","a+")
	downloadRecord.seek(0)
	downloadData=downloadRecord.readlines()


	counter=0;
	maximum=0;

	for line in downloadData:
		if str(addr[1]) in downloadData:
			counter+=1;

	print "download data: ",downloadData
	if(len(downloadData)!=0):
		maximum=(Counter(downloadData).most_common(1))[0][1]

	print "counter", counter, "max: ",maximum
	print "Time sleep is: ",maximum-counter
	# time.sleep(maximum-counter)


	print file2Send
	currentDir=os.getcwd()
	filePath = os.getcwd() + "/uploads"
	# print filePath
	# os.chdir(filePath)
	
	# if os.path.exists(file2Send):
	
	chunkFile=open("chunkRecord.txt","a+")
	chunkFile.seek(0)
	chunkRecord=chunkFile.readlines();

	print chunkRecord
	# print chunkRecord[0],chunkRecord[1]


	os.chdir(filePath)
	fileReq=open(file2Send,"r")
	fileData=fileReq.readlines()
	# print fileData


	print addr
	chunkStart=0;

	if(len(chunkRecord)!=0):
		print "came in chunk"
		for line in chunkRecord:
			print line
			if addr[0]+" "+str(addr[1])+" "+file2Send in line:
				chunkStart=int(line.split(" ",3)[3])
				print "Resume from", chunkStart

			


	length=len(fileData)
	chunkSize=int(length/30)

	print "Chunks size is: ",chunkSize 

	x=chunkStart;

	try:

		for x in range(chunkStart,31):
		
			time.sleep((maximum-counter)*0.5)

			confirm=client.recv(1024)
			# if x is not 30:
			client.send(''.join(fileData[x*chunkSize : (x+1)*chunkSize]))
			# if x is 30:
			# 	print "came in last"
			# 	client.send(''.join(fileData[x*chunkSize:]))
			
			if not confirm:
				break

			# client.recv(1024)
			print "Data sent: ",int ((x/30)*100),"%\n"
			time.sleep(0.1)
			# time.sleep((maximum-counter)*0.5)


	except IOError as e:
		 	print "client is disconnected"
		 	print "sent till: ",x
		 	chunkFile.write(addr[0]+" "+str(addr[1])+" "+file2Send+" "+str(x-1)+"\n")
		 	client.close()
		 	fileReq.close();
		 	chunkFile.close()
			os.chdir(currentDir)
		 	return

	# if(len(chunkRecord)!=0):     //Required to remove those fully downloaded!
	# 	for line in chunkRecord:
	# 		print line
	# 		if addr[0]+" "+str(addr[1])+" "+file2Send in line:


	fileReq.close();
	chunkFile.close()
	downloadRecord.close()
	os.chdir(currentDir)
	client.close()

	chunkF=open("chunkRecord.txt","w")
	for line in chunkRecord:
		if addr[0]+" "+str(addr[1])+" "+file2Send not in line:
			chunkF.write(line)

	chunkF.close()

	# if(len(chunkRecord)!=0):     //Required to remove those fully downloaded!
	# 	for line in chunkRecord:
	# 		print line
	# 		if addr[0]+" "+str(





def listenToTracker(s):


	choice=0;
	choice2=-15
		

	# s = socket.socket()             # Create a socket object
	# s.connect((argv[1],int(argv[2])))
	# address=s.getsockname()
	
	while(1):		
		
		choice=input("Press 1 to send stuff to tracker\nPress 2 to download a file\nPress 3 to break connection with tracker \nPress -1 to quit\n")
		
		if(choice==-1):
			s.send("^^Quiet^^")
			s.close()
			exit()


		if(choice==1):
			s.send("~Sending Torrent File::~")
			time.sleep(.3)
			torrentsPath = os.getcwd() + "/torrents"
			uploadsPath = os.getcwd() + "/uploads"
			createTorrents(uploadsPath, torrentsPath)
			shutil.make_archive("zipped", 'zip', torrentsPath)

			# s = socket.socket()             # Create a socket object
			# s.connect((argv[1],int(argv[2])))

			filename='zipped.zip'
			f = open(filename,'rb')
			l = f.read(1024)

			while (l):
				s.send(l)
				# print('Sent ',repr(l))
				l = f.read(1024)
			f.close()
			s.send("~^~Done Sending~^~")
			print('Done sending')
			s.recv(1024)
			# s.send('Thank you for connecting')
			choice2=input("Press 0 to break connection with tracker \nPress 1 to review menu\n")
			if(choice2==0):
				s.send("^^Quiet^^")
				# s.close()
				# listen(address)


		if(choice==2):
			s.send("~Download mode~");
			reqFile=raw_input("Please enter the required file name: ")
			s.send(reqFile)
			torFile=""

			count=1
			while(1):
				torFile=s.recv(2000)
				if("..Done Sending Torrents.." in torFile):
					break

				reqTorrent=open("reqTorrent"+str(count)+".torrent",'w')
				reqTorrent.write(torFile)

				s.send("Received packet!")
				count+=1;
				reqTorrent.close()

			peersList=[]
			portList=[]

			while(1):      					# Receiving peer ports!

				peerData=s.recv(1024)
				
				# print "Sent peer data: ",peerData
				if("--ALL PEERS SENT--") in peerData:   #18
					break;
				peersList.append(peerData)
				s.send("Received!!")



			# print "peer List",peersList


			for line in peersList:
				portList.append(line.split(" ",2)[1])

			# peerPort=peerData.split(" ",2)[1]
			# peerIp=peerData.split(" ",2)[0]


			# print peerData
			print "Port list: ",portList
			peerNumber=input("Enter the peer number u wanna connect to: ")
			
			if(len(portList)==0):
				print "File doesnot exists!!"
				return

			if(peerNumber > len(portList ) or peerNumber < 0 ):
				print "Invalid input"
				return;

			peerPort=portList[peerNumber-1]

			fileSize=0
			reqTorrent=open("reqTorrent1.torrent","r")
			torrData=reqTorrent.readlines()

			for line in torrData:			#This checks for the file
				if "size" in line:
					fileSize=int(line.split(" ",3)[2])
					break;

			print "file size is: ",fileSize

			# s.send("Received!!")


			# choice2=input("Press 0 to break connection with tracker\n")
			# if(choice2==0):
			# 	s.send("^^Quiet^^")


			# print "till gere"
			m = socket.socket()             # Create a socket object
			m.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

			portChoice=input("Enter the valid port number u wanna bind to: ")
			m.bind(("127.0.0.1",portChoice))

			m.connect(("127.0.0.1",int(peerPort)-2))
			print "till gere"
			got=m.recv(1024)
			print got
			m.send(reqFile)
			
			# content=m.recv(1024)
			# m.send("chunk received!")
			
			fileAsked=open(reqFile,"a+")
			curPath=os.getcwd()
			
			try:

				while 1:

					m.send("receiving")

					content=m.recv(2048)
					print "Data received: ",int ((os.path.getsize(curPath+"/"+reqFile)/fileSize)*100),"%\n"
					if not content:
						break;

					# m.send("chunk received!")
					
					fileAsked.write(content)
					# print "Data received: ",int ((os.path.getsize(curPath+"/"+reqFile)/fileSize)*100),"%\n"

			
				downloadRecord=open("downloadRecord.txt","a+")
				downloadRecord.write(str(int(peerPort)-2)+"\n")

				downloadRecord.close()


			except KeyboardInterrupt:
				print "Came in keyBoard interrupt"
				s.close()
				# fileAsked.write(content)
				m.close()

			

			m.close()
			fileAsked.close()

				# s.close()
				# breakConnection(s)
				# connectWithPeer(peerIp,peerPort,s)
			
		if(choice==3):
			s.send("^^Quiet^^")
			# s.close()
			# listen(address)
			# exit()
				

		choice=-10
		choice2=-10

	# s.close()

def main(argv):

	s = socket.socket()             # Create a socket object
	s.connect((argv[1],int(argv[2])))
	s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	address=s.getsockname()
	
	n = socket.socket()             # Create a socket object
	n.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	host = '127.0.0.1'  
	n.bind((host,int(address[1])-2))           # Bind to the port
	n.listen(5)                     # Now wait for client connection.

	
	start_new_thread(listenToTracker,(s,))

	while 1:
		client, addr = n.accept()     # Establish connection with client.
		start_new_thread(sendToPeer,(client,addr))






if __name__=="__main__":
	main(sys.argv)



