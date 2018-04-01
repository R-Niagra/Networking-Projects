#include <stdio.h> // basic I/O
#include <stdlib.h>
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


//////////////////////////////////////////////////////////////////
while(numbytes!=0)
{
string filename;

if((numbytes = recv(sockfd, buf, BUFLEN-1, 0)) == -1)
{
    cout<<"Failed to receive data"<<endl;
    exit(1);
}
buf[numbytes] = '\0';
printf("Received: %s \n", buf);


cout<<"Please enter your command: ";
getline(cin,mystr);

cout<<"Mystr is: "<<mystr<<endl;
mystr=mystr+"\r\n";

if((io=write(sockfd,mystr.c_str(),mystr.length()))<0)
{
cout<<"Failed to send"<<endl;
exit(1);
}


 if(mystr=="EXIT\r\n" || mystr=="exit\r\n")
	{
close(sockfd);
numbytes=0;
break;
	}
}



  return 0;
}


