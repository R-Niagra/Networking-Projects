#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h> 
#include <sys/socket.h>
#include <netinet/in.h>
#include <iostream>
#include <dirent.h>
#include <stdio.h>
#include <string>
#include <fstream>
#include <sstream>
using namespace std;
int file_size(char* filename)
{
ifstream file( filename, ios::binary | ios::ate);
return file.tellg();

}

//////////////////////////////
void sendFileData(char* filename,int sockfd)
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
 FILE *fs = fopen(filename, "r");



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

////////////////////////////////////////////////////////////
void sendDirectory(int newsockfd)
        {
  int send;
  DIR    *d;
  struct dirent *dir;
  d = opendir(".");
  if (d)
  {
    while ((dir = readdir(d)) != NULL)
    {
      printf("Sending %s\n", dir->d_name);
     sleep(0.7);

	 send=write(newsockfd,dir->d_name,50);
 	if (send < 0)
        {
        printf("ERROR writing to socket");
        }

    }
	cout<<"Files done"<<endl;
	sleep(1);
	send=write(newsockfd,"THE END",7);
    closedir(d);
  }
        }


bool stringCheck(char* buffer,string toCheck)
{
int count=0;
for(int i=0;i<toCheck.length();i++)
	{
if(buffer[i]==toCheck[i])
count++;
	}

return count==toCheck.length();	
}

bool isFilePresent(char* fileName)
{
ifstream infile(fileName);
return infile.good();
}

void shakeHand(int newsockfd,char* buffer)
{
int n,m;
	n = read(newsockfd,buffer,1024);

    if (n < 0)
        {
        printf("ERROR reading from socket");
        }

     printf("RECEIVED:  %s\n",buffer);

    m = write(newsockfd,"I got your message,Welcome",30);
   
     if (m < 0) 
        {
        printf("ERROR writing to socket");
        }






}



//////////////////////////////////////
int main(int argc, char *argv[])
{
     int sockfd, newsockfd, portno;
     socklen_t clilen;
     char buffer[1024];
     struct sockaddr_in serv_addr, cli_addr;
     int n,m;


     bzero(buffer,1024);

     if (argc < 2) {
         fprintf(stderr,"ERROR, no port provided\n");
         exit(1);
     }
     sockfd = socket(AF_INET, SOCK_STREAM, 0);
     if (sockfd < 0) 
        printf("ERROR opening socket");
     bzero((char *) &serv_addr, sizeof(serv_addr));

 portno = atoi(argv[1]);

 if((portno > 65535) || (portno < 2000))
    {
   cout<< "Please enter a port number between 2000 - 65535" << endl;
     return 0;
    }


     serv_addr.sin_family = AF_INET;
     serv_addr.sin_addr.s_addr = INADDR_ANY;
     serv_addr.sin_port = htons(portno);
     if (bind(sockfd, (struct sockaddr *) &serv_addr,sizeof(serv_addr)) < 0) 
            printf("ERROR on binding");


  listen(sockfd,5);
  clilen = sizeof(cli_addr);

  while(1) 
  {
	
	cout<<"Started listening!"<<endl;
     newsockfd = accept(sockfd, 
                 (struct sockaddr *) &cli_addr, 
                 &clilen);
  
	n=1;
	  if (newsockfd < 0) 
	{
          printf("ERROR on accept");
	return 0;
	}
shakeHand(newsockfd,buffer);

//cout<<"New sock in main "<<newsockfd<<endl;

   while(n>0)
	{
	//cout<<"rup"<<endl;
    
      bzero(buffer,2048); 
	cout<<"waiting to receive..."<<endl;
      n = read(newsockfd,buffer,1024);
    
//     cout<<"Starting n val: "<<n<<endl;

     if (n < 0) 
	{
	printf("ERROR reading from socket");
	}

     printf("RECEIVED:  %s\n",buffer);
 
/*    m = write(newsockfd,"I got your message",18);
   
     if (m < 0) 
	{
	printf("ERROR writing to socket");
	}
*/
//cout<<"Buffer is: "<<buffer<<"done"<<endl;

     if(stringCheck(buffer,"list server"))
	{
	sendDirectory(newsockfd);
	}



     if(stringCheck(buffer,"create server "))
	{
	 char filename[50];
	memcpy(filename,&buffer[14],20);
       cout<<"File name is: "<<filename<<endl;

        if(isFilePresent(filename))
                {
        cout<<"ERROR!!! File already exists"<<endl;
	 m = write(newsockfd,"ERROR!!! File already exists",40);

	     if (m < 0)
       		 {
	        printf("--ERROR writing to socket");
       		 }


                }

        else
                {
        ofstream outfile;
        outfile.open(filename);
        cout<<filename<<" Has been created!!"<<endl;
         m = write(newsockfd,"--File has been successfully created!!",40);

             if (m < 0)
                 {
                printf("ERROR writing to socket");
                 }
       
		 }
	}
/////////////////////////////////////////////////////

	if(stringCheck(buffer,"send "))
	{
	char filename1[30];

        memcpy(filename1,&buffer[5],15);
       cout<<"File name is: "<<filename1<<endl;
	

        if(isFilePresent(filename1))
               {
        cout<<"ERROR!!! File already exists"<<endl;
         m = write(newsockfd,"ERROR!!! File already exists",40);

             if (m < 0)
                 {
                printf("--ERROR writing to socket");
                 }
                }
        else
		{

	FILE *file;
	file = fopen(filename1, "w");
	m = write(newsockfd,"File doesnot exists! Plz send data",50);
             if (m < 0)
                 {
                printf("Asked for the valid file data!");
                 }
	 n = read(newsockfd,buffer,1024);

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
	 len = recv(newsockfd,buffer,512,0);	
   	 if (len <= 0)
        {
        printf("No data!!!");
	break;
        }
	fwrite(&buffer,sizeof(char),len,file);
	fileSize-=len;
	
	bzero(buffer,2048);
	    }

	fclose (file);
	cout<<"EXITING while"<<endl;
		}
	}

 if(stringCheck(buffer,"receive "))
     {
	cout<<"came in receive func"<<endl;

        char filename1[30];
        memcpy(filename1,&buffer[8],15);
       cout<<"File name is: "<<filename1<<endl;


        if(!isFilePresent(filename1))
               {
        cout<<"Wait!!! File doesnot exists"<<endl;
         m = write(newsockfd,"ERROR!!! File doesnot exists",40);

             if (m < 0)
                    {
                printf("--ERROR writing to socket");
                    }

                }
	     else
		{
        m = write(newsockfd,"ERROR!!! File does exists.Sending...",40);
		sleep(0.8);
		sendFileData(filename1,newsockfd);
	

		}

   }

if(stringCheck(buffer,"delete server "))
     {
     

        char filename1[30];
        memcpy(filename1,&buffer[14],15);
       cout<<"File name is: "<<filename1<<endl;
	int m=1;
	if(remove (filename1)!=0)
	{
        cout<<"Error deleting the file!!!!"<<endl;
	 m = write(newsockfd,"Error deleting the file!!!!",40);
	
	}
        else
	{
        cout<<"file successfully deleted!!!"<<endl;
	 m = write(newsockfd,"File successfully deleted",40);
	}

             if (m < 0)
                 {
                printf("--ERROR writing to socket");
                 }

    }


     bzero(buffer,2048);
    }
  }







cout<<"Closing socket"<<endl;
 close(newsockfd);
 close(sockfd);

return 0;

}
