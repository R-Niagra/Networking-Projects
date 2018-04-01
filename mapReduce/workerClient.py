import socket
import sys
import os.path
from thread import *
import threading
import time
import Queue

dataRead=[]
checkedTill=0
queryCount1=0
endRange=0;


def finder(parts,q,addr,sock):
	t = threading.currentThread()      #Creating an object
	t.run=True
	global dataRead
	global checkedTill
	global endRange

	query=parts[5]
	print "Query is: ",query
	queryCount=0
	global queryCount1
	fileNum=0;
	rangeStart=parts[3]
	endRange=parts[4]

	print "will check from: ",parts[3]," to ",parts[4]
	print "started searching-------"

	folder_size=0;
	for(path, dirs, files) in os.walk("source"):

		for file in files:
			filename = os.path.join(path, file)
			folder_size += os.path.getsize(filename)

			if(t.run==False):
				print "Quiting!";
				return;

			if(folder_size>=int(parts[3]) and folder_size<=int(endRange)):
				# print "End range is: ",endRange
				checkFile=open(filename,"r")
				fileData=checkFile.readlines()
				checkFile.close()
				putIn=0;
				# print "checking"
				for line in fileData:
					if(query in line):
						# print line
						queryCount+=1;
						putIn=1;
						queryCount1+=1;
						# q.put(filename)
						# dataRead.append(folder_size)
						# break;

				# putIn=fileData.count(query)
				if(putIn>=1):
					q.put(filename)
					queryCount+=putIn
					putIn=0;

				fileNum+=1;
				dataRead.append(folder_size)


				# print fileData
			# time.sleep(0.2)
	print "Files checked: ",fileNum, " Query count: ",queryCount
	if(len(dataRead)>0):
		checkedTill=dataRead[-1]

	sock.sendto("15440,-,5,%s,%d,%s,%d" %(rangeStart,checkedTill,query,queryCount),addr)



def main(argv):

	sock=socket.socket(socket.AF_INET,socket.SOCK_DGRAM) 
	sip=argv[1]
	sport=int(argv[2])
	addr=(sip,sport)
	sock.setblocking(0)
	sock.sendto("15440,-,1,-,-,-,-",addr)

	ping=time.time()+60*3

	result=[]
	q = Queue.Queue()
	# dataRead=Queue.LifoQueue()    #Corrosponding to the chunks that has been read!
	global checkedTill
	global dataRead
	global queryCount1
	global endRange
	start=0
	end=0
	searchStart=0;
	query=""

	while(True):

		try:

			data,addr=sock.recvfrom(1024)

		except socket.error as error:

			if "[Errno 35]" in str(error):
				# if(time.time()>=ping):
				# 	sock.sendto("15440,-,3,-,-,-,-",addr) 

				continue

			else:
				raise error


		print "data: ",data
		parts=data.split(",")

		if(parts[2]=="2"):
			print "job received! Sending confirmation: "
			start=int(parts[3])
			end=int(parts[4])
			sock.sendto("15440,-,3,-,-,-,-",addr)    # job confirmation

# ping=time.time()+3;

	# if(threading.active_count()==1):
			searchStart=int(parts[3])
			query=parts[5]

			print "threading count: ",threading.active_count()

			if(threading.active_count()==1):
				t = threading.Thread(target=finder, args=(parts,q,addr,sock))
				t.start()

			else:
				print "coming in else condition"
				endRange=int(parts[4])


			# print "threading count later: ",threading.active_count()


# if()
# 	t.do_run = False
#  			t.join()
	# Start from new range


		if(parts[2]=="0"):
			print "Received ping! Sending reply updates::"
			current=""


			if(len(dataRead)>0):
				# print "dataRead: ",dataRead
				checkedTill=dataRead.pop();
				print "Checked till: ",checkedTill
				dataRead=[]

			if(q.qsize()>0):
				limit=q.qsize();
				for val in range(limit):
					x=q.get();
					print "result in: ",x
					current+=(x+"|<->|")
					result.append(x)   #Maintaining its current result state

			print "query count is: ",queryCount1
			current=current+str(queryCount1)
			queryCount1=0
			# if(dataRead.qsize()>0):
			# 	checkedTill=dataRead.get();
			# 	dataRead=[]
			print "Sending: ",current		
			sock.sendto("15440,-,6,%d,%d,%s,%s" %(searchStart,checkedTill,query,current),addr)		


		if(parts[2]=="8"):             #Cancel job command!!
			print "job has been cancelled!!"

			t.run=False		       # Thread will stop running if cancel commad fiven or essentially new command comes			
			t.join()
			return
# print "hello",q.get()		


if __name__=="__main__":
	main(sys.argv)





