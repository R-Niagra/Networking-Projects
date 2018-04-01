import socket
import sys
import os
from thread import *

def clientthread(client,default):
	client.send("Server: Welcome to CS 382 search engine! Please enter your search Query:")
	query=client.recv(2000)     # this value is the buffer capacity
	print query

	while(1):

		os.chdir(default)
		serverPath=os.getcwd()
		bbcPath=serverPath+"/bbcsport"

		files=os.listdir(bbcPath)
		#print files
		for i in range(1,len(files)):

			if('.' not in files[i]):
				newPath=bbcPath+'/'+files[i]
				os.chdir(newPath)					
				newFiles=os.listdir(newPath)
				for f in range(0,len(newFiles)):
					if(query in newFiles[f]):
						currentPath=os.getcwd()+"/"+newFiles[f]
						posit=currentPath.find("bbcsport")
						slicedPath=currentPath[posit:]
						client.send(slicedPath)
						
					if(newFiles[f][-3:]=='txt' or newFiles[f][-3:]=='TXT'):	 #It ensures that file is txt
						with open(newFiles[f],'r') as infile:
							fileData=infile.readlines()
						for line in fileData:
							if query in line:
								currentPath=os.getcwd()+"/"+newFiles[f]
								posit=currentPath.find("bbcsport")
								slicedPath=currentPath[posit:]
								client.send(slicedPath)      #This is the shortened path sent to the client
								client.send(''.join(fileData))
								break

			elif('.'in files[i]):
				os.chdir(bbcPath)
				if(query in files[i]):
					currentPath=os.getcwd()+"/"+files[i]
					posit=currentPath.find("bbcsport")
					slicedPath=currentPath[posit:]
					client.send(slicedPath)
			
				if(newFiles[f][-3:]=='txt' or newFiles[f][-3:]=='TXT'):	
					with open(files[i],'r') as infile:
						fileData=infile.readlines()
					for line in fileData:
						if query in line:
							currentPath=os.getcwd()+"/"+files[i]
							posit=currentPath.find("bbcsport")
							slicedPath=currentPath[posit:]
							client.send(slicedPath)
							client.send(''.join(fileData))
							break

		client.send("$$-Done-$$")     #This is a signal that search is finished

		while(1):
			folder=client.recv(2024)
			print folder
			if(folder=="exit"):
				client.close()
				return 
			fnd=folder.rfind("/")       #Finds / in reverse manner to extract file name and path
			downloadD=bbcPath+"/"+folder[0:fnd]
			os.chdir(downloadD)
			print os.getcwd()
			allFiles=os.listdir(downloadD)
			print folder[fnd+1:]
			if(folder[fnd+1:] in allFiles):

				with open(folder[fnd+1:],'r') as infile:
					fileData=infile.readlines()
				client.send(''.join(fileData))	
				if(os.stat(folder[fnd+1:]).st_size == 0):
					client.send("empty file")

			else:
				client.send("File doesnot exists!!")

			
		
		

def main(argv):

	ip='127.0.0.1'
	s=socket.socket()
	s.bind((ip,int(argv[1])))
	default=os.getcwd()

	while 1:
		s.listen(5)
		client,add=s.accept()
		start_new_thread(clientthread,(client,default))	
	

	client.close()
	s.close()	


if __name__=="__main__":
	main(sys.argv)





