import sys
import socket
import os
import time
from thread import *
import threading
import path
import random
import threading
import Queue
from os import path
from collections import Counter
import ast

# if os.path.isdir("arch")==1:
# 		print"yes dir"            						
# 	if os.path.isfile("COPYING"):
# 		print"yes file"

																
def findSize(source):     #Checks for the size of the source file
 	numOfFiles=0;
	folder_size=0;
	for(path, dirs, files) in os.walk(source):

		for file in files:
			filename = os.path.join(path, file)
			# print "fname: ",filename
			folder_size += os.path.getsize(filename)
			numOfFiles+=1;

	# print "Total number of files: ",numOfFiles
	return folder_size		


def reAssignJob(wcData,sock):     #[time,addr,[chunk range], timesAssigned,query,accepted,searched,jobDone,pingsDiscarded]
	

	string="15440,-,2,%d,%d,%s,-" %(wcData[2][0], wcData[2][1], wcData[4])
	print "wcData in reassign: ",wcData

	sock.sendto(string,wcData[1])
	wcData[3]+=1;
	wcData[0]=time.time()+8
	return wcData

def send2Client(sock,qResults,clients,query):
	t = threading.currentThread() 
	# print "in thread: ",qResults,"query",query
	# print "clients are: ",clients


	resIndex=0
	clientIndex=0
	for x in range(len(qResults)):
		if(qResults[x][0]==query):
			resIndex=x;

	for y in range(len(clients)):
		if (query==clients[y][2]):
			clientIndex=y

	clientAddr=clients[clientIndex][1]
				#start sending the results
	sock.sendto("%s queries found in the data" %str(qResults[resIndex][1]),clientAddr)
	for z in range(2,len(qResults[resIndex])):
		checkFile=open(qResults[resIndex][z],"r")
		fileData=checkFile.readlines()
		checkFile.close()

		for line in fileData:
			if(query in line):
				sock.sendto("%s: %s"%(qResults[resIndex][z],line),clientAddr)

	del qResults[resIndex]
	return qResults


def main(argv):


	ip='127.0.0.1'
	port=int(argv[1])

	sock=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
	sock.bind((ip,port))
	sock.setblocking(0)
	# sock.settimeout(5)
	# rcPing=time.time()+60*5      #Rquest client ping
	serverState=time.time()+20
	wcData=[]					#Worker client ping
	
	curDir=os.getcwd()
	job=[]                     # [Query,start,endSearch]
	qResults=[]
	clients=[]					#[client,addr,query]
	wcTimeSpan=0
	activeQworker=[]           #[Query,activeWorkerWorking]
	
	deleteCommand=0
	popular=""
	popularResult=[]
	chunkLength=0;
	fileSize=0;
	qHistory=[]
	query=""
	jobless=[]      #Against jobless workers
	onJob=[]		#Against in job workers

	if("myState.txt" in os.listdir(os.getcwd())):
		startFile=open("myState.txt","r")
		startData=startFile.readlines()
		startFile.close()
		print startData
		print startData[0]
		wcData = ast.literal_eval(startData[0])
		job=ast.literal_eval(startData[1])
		qResults=ast.literal_eval(startData[2])
		jobless=ast.literal_eval(startData[3])
		onJob=ast.literal_eval(startData[4])
		activeQworker=ast.literal_eval(startData[5])
		# wcData=startData[0]

	while(True):
		try:

			data,addr=sock.recvfrom(3072)	
		except socket.error as error:

			if "[Errno 35]" in str(error):

				# print "time is: ",time.time()

				for x in range(len(clients)):		
					if(time.time()>clients[x][0]):
						print "Request client connection has gone skeptical...Breaking Connection!! "
						deleteCommand=1
						sock.sendto("15440,-,8,-,-,-,-",clients[x][1])
						rmv=0
						for x in range(len(wcData)):
							if(wcData[x][4]==clients[x][1]):
								sock.sendto("15440,-,8,-,-,-,-",wcData[x][1])
								rmv+=1
						for y in range(len(activeQworker)):
							if(activeQworker[y][0]==clients[x][1]):
								activeQworker[y][1]-=rmv


					if(x==len(clients)-1 and deleteCommand==1):
						del clients[x]
						deleteCommand=0;	
						# return;

				if(len(qHistory)>=1):
					popular=(Counter(qHistory).most_common(1))[0][0]
					# print "popular is: ",popular

				if(time.time()>serverState):
					myFile=open("myState.txt","w")
					print "Updating state"
					myFile.write(str(wcData)+"\n");
					myFile.write(str(job)+"\n");
					myFile.write(str(qResults)+"\n");
					myFile.write(str(jobless)+"\n");
					myFile.write(str(onJob)+"\n");
					myFile.write(str(activeQworker)+"\n");

					myFile.close()
					serverState=time.time()+30


				if(len(qResults)>0):
					for z in range(len(qResults)):
						if(popular==qResults[z][0]):
							popularResult.append(qResults[z])

					valid=1
					# print "check1"
					for x in range(len(activeQworker)):
						# print "check2"
						if(activeQworker[x][1]<=0):
							for y in range(len(job)):
								# print "job detected"
								if(activeQworker[x][0]==job[y][0]):
									valid=0
							if(valid==1 and threading.active_count()==1 and len(qResults)>0):
								print "check4"

								#Search has been already completed send result to client
								# start_new_thread(send2Client,(sock,qResults,clients,activeQworker[x][0]))
								t = threading.Thread(target=send2Client, args=(sock,qResults,clients,activeQworker[x][0]))
								t.start()


				if(len(wcData)> 0):
					for x in range(0,len(wcData)):


						# print "Main data: ",wcData[x]

						if (time.time()> wcData[x][0] and wcData[x][3]<3 and wcData[x][5]==0):
							print "resending job until 3 time"
							wcData[x]=reAssignJob(wcData[x],sock)
							# print "wcData later: ",wcData
						elif(wcData[x][3]>=3):
							print "Gonna delete this dead node: ",wcData[x][1]
							deleteCommand=1;
							sock.sendto("15440,-,8,-,-,-,-",wcData[x][1])

							# del wcData[x]    Will delete down

						if(time.time()>=wcData[x][0] and wcData[x][8]<3):
							print "Ping not answered. Resending!!!"

							sock.sendto("15440,-,0,-,-,-,-",wcData[x][1])
							wcData[x][0]+=14;
							wcData[x][8]+=1;
						
						elif(time.time()>=wcData[x][0] and wcData[x][8]>=3):
							print "Connection of: ",wcData[x][1]," has gone skeptical. Disconnecting with the worker!!"	
							#putting the job left by the worker into the job Queue
							sock.sendto("15440,-,8,-,-,-,-",wcData[x][1])

							job.append([wcData[x][4],int(wcData[x][6]),int(wcData[x][2][1])])

							for z in range(len(activeQworker)):
								if(activeQworker[z][0]==wcData[x][4]):    #Active worker decreases
									activeQworker[z][1]-=1;         

							# print "deleting data of this worker: "
							deleteCommand=1;
							# del wcData[x] Will delete down



						if(time.time()>=(wcData[x][0]-5) and wcData[x][5]==1 and time.time()>=wcTimeSpan):  #Worker client has confirmed job req Now
							#Ping worker client
							sock.sendto("15440,-,0,-,-,-,-",wcData[x][1])
							# wcData[x][0]+=0.1;
							wcTimeSpan=time.time()+3


					#If there is a job divide equally among jobless
				if(len(job)>0 and len(jobless)>0 ):
						#assign task to free workers
					for y in range(len(job)):

						currentJob=job.pop();

						allowedWorkers=0;
						query=currentJob[0]

						print "active worker: ",activeQworker
						print "current job: ",currentJob


						for z in range(len(activeQworker)):
							if(activeQworker[z][0]==currentJob[0]):   #If queries are equall
								allowedWorkers=5-activeQworker[z][1]


						if(len(jobless)>0 and len(jobless)<allowedWorkers):
							chunkLength=(currentJob[2]-currentJob[1])/(len(jobless))
						if(len(jobless)>allowedWorkers):
							chunkLength=(currentJob[2]-currentJob[1])/allowedWorkers

						# for z in range(len(wcData)):
							# if()

						curChunk=currentJob[1];
						for x in range(0,allowedWorkers):				

							if(x>=len(jobless)):
								break
							onJob.append(jobless[x])
							# onJob[x][1]=random.randint(0,1000)
							print "Connecting to: ",jobless[x][0]
							string="15440,-,2,%d,%d,%s,-" %(curChunk, (curChunk+chunkLength), query)
							sock.sendto(string,jobless[x][0])
							
							wcData.append([(time.time()+7),jobless[x][0],[curChunk,curChunk+chunkLength],1,query,0,curChunk,0,0])
							#[time,addr,[chunk range], timesAssigned,query,accepted,searched,jobDone,unansweredPings]
							#[time,addr,[chunk range], timesAssigned,query,accepted,searched,jobDone,pingsDiscarded]
							for z in range(len(activeQworker)):
								if(activeQworker[z][0]==query):
									activeQworker[z][1]+=1

							curChunk=curChunk+chunkLength

						for y in range(0,len(onJob)):
							if onJob[y] in jobless:
								jobless.remove(onJob[y])

				if(len(activeQworker)>0 and len(jobless)>0):     #There are more than 1 search query		
					for x in range(len(activeQworker)):
						if(activeQworker[x][1]>=5):
							continue
						else:
							currentProgress=[]
							#assign him some part of work to new worker!!!
							for y in range(len(wcData)):
								currentProgress.append(wcData[y][2][1]-wcData[y][6])
							maxVal=max(currentProgress)    #Max data left to be searched
							maxIndex=currentProgress.index(maxVal)

							if(maxVal<50000000):   #If the chunk is too short just skip
								continue

							#Assign to new worker and update prev worker
							# string="15440,-,2,%d,%d,%s,-" %(curChunk, (curChunk+chunkLength), query)
							primaryLimit=maxVal/2+wcData[y][6]
							string="15440,-,2,%d,%d,%s,-" %(0,primaryLimit, wcData[maxIndex][4])							
							sock.sendto(string,wcData[maxIndex][1])
							
							secondaryLimit=primaryLimit+maxVal/2;
							string1="15440,-,2,%d,%d,%s,-" %(primaryLimit, (secondaryLimit),wcData[maxIndex][4])
							sock.sendto(string1,jobless[0][0])
							onJob.append(jobless[0])

							for z in range(len(activeQworker)):
								if(activeQworker[z][0]==wcData[maxIndex][4]):
									activeQworker[z][1]+=1

							for y in range(0,len(onJob)):
								if onJob[y] in jobless:
									jobless.remove(onJob[y])



				if(deleteCommand==1):
					del wcData[x];
					deleteCommand=0;

				continue
			else:
				raise error

		# print "came out"
		# print "Data: ",data
		parts=data.split(",");
		# print "qResults: ",qResults
		# print "activeQworker",activeQworker
		# print "wcData",wcData
		# print "clients",clients

		if(parts[2]=="-1"):      #Client connected
			
			query=parts[5]
			qHistory.append(query)
			clients.append([time.time()+15,addr,query])    #<---
			
			if(query==popular):
				t = threading.Thread(target=send2Client, args=(sock,popularResult,clients,query))
				# t.start()
				continue



			qResults.append([query,0])
			activeQworker.append([query,0])

			if(fileSize==0):
				fileSize=findSize("source")
				fileSize=150000000

			if(len(jobless)==0):
				print "No worker client connected(available) right now!! Wait a sec"
				job.insert(0,[query,0,fileSize])   #Job will be queued
				print "job len: ",len(job)

			if(len(jobless)>0 and len(jobless)<5):
				chunkLength=fileSize/(len(jobless))
			if(len(jobless)>5):
				chunkLength=fileSize/5

			curChunk=0;
			for x in range(0,5):				
				if(x>=len(jobless)):
					break

				onJob.append(jobless[x])
				# onJob[x][1]=random.randint(0,1000)
				print "Connecting to: ",jobless[x][0]
				string="15440,-,2,%d,%d,%s,-" %(curChunk, (curChunk+chunkLength), query)
				sock.sendto(string,jobless[x][0])
				activeQworker[-1][1]+=1;       #Will add to last worker
				print "increased"
				wcData.append([(time.time()+8),jobless[x][0],[curChunk,curChunk+chunkLength],1,query,0,curChunk,0,0])
				#[time,addr,[chunk range], timesAssigned,query,accepted,searched,jobDone,unansweredPings]
				curChunk=curChunk+chunkLength
				print "active workers: ",activeQworker

			for y in range(0,len(onJob)):
				if onJob[y] in jobless:
					jobless.remove(onJob[y])
					onJob[y][1]=random.randint(0,1000)

			print "file size is: ", fileSize

			# rcPing=0
			# rcPing=time.time()+15      #Request client ping time ends at


		if(parts[2]=="0"):		#Against the ping
			for z in range(len(clients)):
				if(addr==clients[z][1]):
					print "reseting clients ping"
					clients[z][0]=time.time()+15


		if(parts[2]=="1"):      #When worker clients joins
			jobless.append([addr,0])
			print "jobless are: ",jobless
			print "length of jobless: ",len(jobless)

		if (parts[2]=="3"):   #confirmation of the job
			for x in range(0,len(wcData)):
				if(addr==wcData[x][1]):
					# print "resetting wc time of",addr," wcdata",wcData[x] 
					# wcData[x][0]=wcData[x][0]+3

					wcData[x][5]=1;
					# print "later: ",wcData[x]

		if(parts[2]=="6"):
			# print "Search ",parts[6]
			# print "Search done till: ",parts[3],"---",parts[4]
			
			for y in range(len(wcData)):
				if(wcData[x][1]==addr):
					wcData[x][0]=time.time()+10


			for x in range(len(wcData)):
				if(wcData[x][1]==addr):      #Updating the chunks read			
					print "updating chunks: ",parts[4]

					wcData[x][6]=int(parts[4])
					# print "Updated: ",wcData[x]

			for x in range(len(qResults)):
				if(qResults[x][0]==parts[5]):
					results=parts[6].split("|<->|")
					# qResults[x].append(results);
					for y in range(len(results)-1):
						# print "results are: ",results[y]
						qResults[x].append(results[y])     #Results against query

					# print "result length: ", results[len(results)-1]
					# print "qResults are: ",qResults
					# qResults[x][1]=qResults[x][1]+int(results[len(results)-1]) <<<<<<<<-------

		if(parts[2]=="5"):

			for z in range(len(qResults)):
				if(qResults[z][0]==parts[5]):
					qResults[z][1]+=int(parts[6])


			# Worker client Successfulyy completed search
			print "job done by: ",addr
			# for x in range(len(wcData)):
			# 	if(wcData[x][1]==addr):
			# 		wcData[x][7]=1;
			print "final qResults: ",qResults
			# print "on job: ",onJob
			for y in range(len(onJob)):
				if(onJob[y][0]==addr):
					jobless.append(onJob[y])
					# onJob.remove(onJob[y])    #<<<<---------

			for y in range(0,len(jobless)):
				if jobless[y] in onJob:
					onJob.remove(jobless[y])

			# print "on job: ",onJob
			# print "on job: ",jobless
			for z in range(len(activeQworker)):
				if(activeQworker[z][0]==parts[5]):
					print "decreased"
					activeQworker[z][1]-=1

			for x in range(len(wcData)):
				if(wcData[x][1]==parts[1]):
					del wcData[x]                #Current progress deleted by when job is done

			print "activeQworker after completing job: ",activeQworker

			#Also delete from wcData
			#Also uodate activeQworker


if __name__=="__main__":
	main(sys.argv)

