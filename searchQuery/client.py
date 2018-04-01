import socket
import sys
from termcolor import colored


def main(argv):
	cl=socket.socket()
	cl.connect((argv[1],int(argv[2])))
	welcome=cl.recv(2000)
	print welcome
	query=raw_input()
	cl.send(query)
	data=""
	while(1):
		data=cl.recv(3000)
		#print data
		mylines = data.splitlines()    #This part is rendered for colour change
		for j in mylines:
			mywords = j.split()
			for i in mywords:
				if i==query:
					print colored(i, 'red'),
				else:
					print (i),
			print ''		
		folder=""                  #Till here!!!
		if data[-10:]=="$$-Done-$$":
			while(1):
				print("Please enter the folder name to download or press exit: ")
				folder=raw_input()
				fnd=folder.find("/")        # This looks for the only file name given(Without directory)
				
				while (folder.count("/")!=1 and folder!="exit"):
					print "Please enter acceptiple format again: "
					folder=raw_input()

				cl.send(folder)
				if(folder=="exit"):
					break
				fileData=cl.recv(2024)
				#print fileData
				# print colored(fileData, 'red')
				if(fileData!="File doesnot exists!!" and fileData!="empty file"):	
					file=open(folder[fnd+1:],'w')
					file.write(fileData)
				else:
					print fileData			

		if(folder=="exit"):
			cl.close()
			break			

if __name__=="__main__":
	main(sys.argv)



