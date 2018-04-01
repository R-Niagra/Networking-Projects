#include <unistd.h>
#include <stdio.h> // basic I/O
#include <stdlib.h>
#include <sstream>
#include <cstdlib>
#include <sys/types.h> // standard system types
#include <netinet/in.h> // Internet address structures
#include <sys/socket.h> // socket API
#include <arpa/inet.h>
#include <netdb.h> // host to IP resolution
#include <string.h>
#include <unistd.h>
#include <dirent.h>
#include <stdio.h>
#include <fstream>
#include <string>
#include <iostream>

using namespace std;

#define HOSTNAMELEN 40 // maximal host name length; can make it variable if you want
#define BUFLEN 1024 // maximum response size; can make it variable if you want
//#define PORT argv[2] // port of daytime server

void recvData(char* filename1,int sockfd)
 {
char buffer[1024];
int m=1,n=1;
 FILE *file;
        file = fopen(filename1, "w");
/*        m = write(sockfd,"waiting to get File...",50);
             if (m < 0)
                 {
                printf("Asked for the valid file data!");
                 } */

         n = read(sockfd,buffer,1024);

         if (n < 0)
        {
        printf("ERROR reading from socket");
        }
        int fileSize=atoi(buffer);
        cout<<"File size: "<<fileSize<<endl;

        sleep(0.5);
        ssize_t len;
        while(fileSize>0)
            {
         len = recv(sockfd,buffer,512,0);
         if (len <= 0)
        {
        printf("No data!!!");
        break;
        }
        fwrite(&buffer,sizeof(char),len,file);
        fileSize-=len;
        bzero(buffer,1024);
            }

        fclose (file);
        cout<<"EXITING while"<<endl;
    }
     

void printDirectory()
	{

  DIR    *d;
  struct dirent *dir;
  d = opendir(".");
  if (d)
  {
    while ((dir = readdir(d)) != NULL)
    {
      printf("%s\n", dir->d_name);
    }

    closedir(d);
  }
	}

void shakeHand(char* buf,int numbytes,int sockfd)
   {

int io;

if((io=write(sockfd,"Hello!!",20))<0)
{
cout<<"Failed to send"<<endl;
exit(1);
}

if((numbytes = recv(sockfd, buf, BUFLEN-1, 0)) == -1)
{
    cout<<"Failed to receive data"<<endl;
    exit(1);
}


buf[numbytes] = '\0';
printf("Received: %s \n", buf);


   }

bool stringCheck(char* buffer,string toCheck)
{
//cout<<"buff: "<<buffer<<endl;
int count=0;
for(int i=0;i<toCheck.length();i++)
        {
if(buffer[i]==toCheck[i])
count++;
        }

return count==toCheck.length();
}
///////////////////////////////////////////
bool isFilePresent(string fileName)
{
ifstream infile(fileName.c_str());
return infile.good();
}
//////////////////////////////////////////
int file_size(string filename)
{
ifstream file( filename.c_str(), ios::binary | ios::ate);
return file.tellg();

}

/////////////////////////////////////////////
void sendFileData(string filename,int sockfd)
{
int index=0,w;
string line="",fileData="",fsize="";
//ifstream infile(filename.c_str());
int fileSize=file_size(filename);
stringstream ss;
ss<<fileSize<<endl;
fsize=ss.str();


  if(w=write(sockfd,fsize.c_str(),fsize.length())<0)
        {
        cout<<"Failed to send"<<endl;
        exit(1);
        }
sleep(0.7);
cout<<"File size is: "<<fileSize<<endl;
 FILE *fs = fopen(filename.c_str(), "r");



char data[512];
int block,byteSent=0;
int bread=0;
int ind=0;
	while(1)
   	{
   int bread=fread(data,sizeof(char),512,fs);
	
	if(bread<=0)
	break;

int bytes_written=0;
char *p=data;
 while (bread > 0) {
         bytes_written = write(sockfd, p, bread);      
	 bread -= bytes_written;
        p += bytes_written;
    }

   }
sleep(0.5);

}

//////////////////////////////////////////////
int main(int argc, char *argv[])
{
  // define your variables here
int sockfd, numbytes,PORT,io;
char buf[BUFLEN];
struct hostent *serv;
// connector’s address information
struct sockaddr_in their_addr;
PORT=atoi(argv[2]);
//printf("Port is: ",PORT);


  // check that there are enough parameters
  if (argc != 3)
    {
     fprintf(stderr, "Usage: mydaytime <hostname>\n");
      exit(-1);
    }

  // Write your code here

if((serv=gethostbyname(argv[1])) == NULL)
{
    cout<<"Error in hostName"<<endl;
    exit(1);
}

if((sockfd = socket(AF_INET, SOCK_STREAM, 0)) == -1)
{
cout<<"Error in creating socket"<<endl;
return 0;
}

their_addr.sin_family = AF_INET;
their_addr.sin_port = htons(PORT);
their_addr.sin_addr = *((struct in_addr *)serv->h_addr);
memset(&(their_addr.sin_zero), '\0', 8);
/////////////////////////////////////////

if(connect(sockfd, (struct sockaddr *)&their_addr, sizeof(struct sockaddr)) <0)
{
    cout<<"Connection failed to establish"<<endl;
    exit(1);
}
else
     cout<<"Connection established!!!!"<<endl;

string mystr="";
numbytes=1;

shakeHand(buf,numbytes,sockfd);

//////////////////////////////////////////////////////////////////
while(numbytes!=0)
{
string filename;

cout<<"Please enter your command: ";
getline(cin,mystr);

cout<<"Mystr is: "<<mystr<<endl;

if (mystr=="list client")
	{
    printDirectory();
	}
/////////////////////////////
else if(mystr=="list server")
	{

if((io=write(sockfd,"list server",11))<0)
{
cout<<"Failed to send"<<endl;
exit(1);
}
    int rcv=1;
	while(!stringCheck(buf,"THE END"))
		{
	if((rcv = recv(sockfd, buf, BUFLEN-1, 0)) == -1)
	{cout<<"Failed to receive data"<<endl;
    	exit(1);}
	
		buf[rcv] = '\0';
		printf("Received: %s \n", buf);
			
		}
	}
///////////////////////////////////

//string filename;

else if(mystr.substr(0,14)=="create client ")
	{
	filename=mystr.substr(14,mystr.length()-14);
	cout<<"File name is: "<<filename<<endl;

	if(isFilePresent(filename))
		{
	cout<<"ERROR!!! File already exists"<<endl;	
		}

	else
		{
	ofstream outfile;
	outfile.open(filename.c_str());
	cout<<filename<<" Has been created!!"<<endl;
		}
	}

else if(mystr.substr(0,14)=="create server ")
	{
int w;
	
	if((io=write(sockfd,mystr.c_str(),mystr.length()))<0)
	{
	cout<<"Failed to send"<<endl;
	exit(1);
	}

	if((numbytes = recv(sockfd, buf, BUFLEN-1, 0)) == -1)
	{
	    cout<<"Failed to receive data"<<endl;
	    exit(1);
	}


	buf[numbytes] = '\0';
	printf("Received: %s \n", buf);


	}
//////////////////////////////////////
else if(mystr.substr(0,5)=="send ")
{
	int w;
        string fileData;
	cout<<"mystr"<<mystr<<endl;
	filename=mystr.substr(5,mystr.length()-5);
	 cout<<"File name is: "<<filename<<endl;

	 if((io=write(sockfd,mystr.c_str(),mystr.length()))<0)
        {
        cout<<"Failed to send"<<endl;
        exit(1);
        }
	sleep(0.2);

        if((numbytes = recv(sockfd, buf, BUFLEN-1, 0)) == -1)
        {
            cout<<"Failed to receive data"<<endl;
            exit(1);
        }
        buf[numbytes] = '\0';
        printf("Received: %s \n", buf);

	if(!stringCheck(buf,"ERROR!!! File already exists"))	
	sendFileData(filename,sockfd);
	
	
}

else if(mystr.substr(0,8)=="receive ")
 {

  int w;
        string fileData;
        cout<<"mystr"<<mystr<<endl;
        filename=mystr.substr(8,mystr.length()-8);
         cout<<"File name is: "<<filename<<endl;

	if(isFilePresent(filename))
	{
	cout<<"Wait!! File already exists!!"<<endl;
	cout<<"Press 1 for override: "<<endl;
	cout<<"Press 0 to to stop this: ";
	string x="";
	getline(cin,x);
	if(x=="0")
	continue;
	}





         if((io=write(sockfd,mystr.c_str(),mystr.length()))<0)
        {
        cout<<"Failed to send"<<endl;
        exit(1);
        }
        sleep(0.2);

        if((numbytes = recv(sockfd, buf, BUFLEN-1, 0)) == -1)
        {
            cout<<"Failed to receive data"<<endl;
            exit(1);
        }
        buf[numbytes] = '\0';
        printf("Received: %s \n", buf);
	
	char filename1[30];
	for(int i=0;i<filename.length();i++)
	filename1[i]=filename[i];


        if(!stringCheck(buf,"ERROR!!! File doesnot exists"))
	{
	   recvData(filename1,sockfd);

	}

 }


else if(mystr.substr(0,14)=="delete client ")
{
        cout<<"mystr"<<mystr<<endl;
        filename=mystr.substr(14,mystr.length()-14);
         cout<<"File name is: "<<filename<<endl;
	
	if(remove (filename.c_str())!=0)
	cout<<"Error deleting the file!!!!"<<endl;
	
	else
	cout<<"file successfully deleted!!!"<<endl;    


}

else if(mystr.substr(0,14)=="delete server ")
{

  if((io=write(sockfd,mystr.c_str(),mystr.length()))<0)
        {
        cout<<"Failed to send"<<endl;
        exit(1);
        }
        sleep(0.2);

        if((numbytes = recv(sockfd, buf, BUFLEN-1, 0)) == -1)
        {
            cout<<"Failed to receive data"<<endl;
            exit(1);
        }
        buf[numbytes] = '\0';
        printf("Received: %s \n", buf);


}


else if(mystr=="EXIT" || mystr=="exit")
	{
close(sockfd);
numbytes=0;
break;
	}

 else
    cout<<"Just Try Again!!!"<<endl;


}



  return 0;
}

