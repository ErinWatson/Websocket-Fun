#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netdb.h> 


/*
ws api
struct ws
ws* ws_init()
	calls hw_init(function pointer)
	register_message_received
	mallocs memory for ws struct
	returns pointer to ws struct

ws_delete()
	calls disconnect (if not already done)
	frees ws struct
ws_connect()
	calls hw_write...

ws_disconnect
	calls hw disconnect
ws_send
	calls hw_write(GET http...)

ws_start_read(ws_message_received function pointer)
	// checks for connection first
	calls hw_start_read(ws_message_received)
	
ws_message_received(char* message)
_____________________________________

hw api

int hw_init
	linux - socket setup
	-1 for error

int hw_write(char* )
	returns num chars written
	-1 for error

hw_disconnect
	-1 for error

hw_start_read(callback)
	for wifi module, register fnction pointer for interrupt
	linux -> start reading call in another thread & register callback
		new thread
			while(1)
				string = read
				call function pointer(string)
				?thread safety issues?
*/


void error(const char *msg)
{
	perror(msg);
	exit(0);
}

int main(int argc, char *argv[])
{
	int sockfd, portno, n;
	struct sockaddr_in serv_addr;
	struct hostent *server;

	char buffer[256];
	if (argc < 3) {
		fprintf(stderr,"usage %s hostname port\n", argv[0]);
		exit(0);
	}

	portno = atoi(argv[2]);
	sockfd = socket(AF_INET, SOCK_STREAM, 0);
	if (sockfd < 0) {
		error("ERROR opening socket");
	}

	server = gethostbyname(argv[1]);
	if (server == NULL) {
		fprintf(stderr,"ERROR, no such host\n");
		exit(0);
	}
	
	bzero((char *) &serv_addr, sizeof(serv_addr));
	serv_addr.sin_family = AF_INET;
	bcopy((char *)server->h_addr, (char *)&serv_addr.sin_addr.s_addr, server->h_length);
	serv_addr.sin_port = htons(portno);
	if (connect(sockfd,(struct sockaddr *) &serv_addr,sizeof(serv_addr)) < 0) {
		error("ERROR connecting");
	}
	
	// todo fix this - so inefficient
	sprintf(buffer,"GET / HTTP/1.1\r\n");
	sprintf(buffer + strlen(buffer), "Connection: Upgrade\r\n");
	sprintf(buffer + strlen(buffer), "Upgrade: websocket\r\n");
	sprintf(buffer + strlen(buffer), "Host: 127.0.0.1:9090\r\n");
	sprintf(buffer + strlen(buffer), "Sec-WebSocket-Protocol: chat, superchat\r\n");
	sprintf(buffer + strlen(buffer), "Sec-WebSocket-Key: L159VM0TWUzyDxwJEIEzjw==\r\n");
	//printf("Sec-WebSocket-Protocol: chat, superchat\r\n");
	sprintf(buffer + strlen(buffer), "Sec-WebSocket-Version: 13\r\n\r\n");
	
	//printf("Please enter the message: ");
	//bzero(buffer,256);
	//fgets(buffer,255,stdin);
	n = write(sockfd,buffer,strlen(buffer));
	if (n < 0) {
		 error("ERROR writing to socket");
	}
	while(1) {
		bzero(buffer,255);
		n = read(sockfd,buffer,255);
		if (n < 0) {
			 error("ERROR reading from socket");
		}
		
		printf("%s\n",buffer);
	}
	close(sockfd);
	return 0;
}