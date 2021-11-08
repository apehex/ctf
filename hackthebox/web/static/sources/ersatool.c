#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>
#include <unistd.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <libgen.h>
#include <sys/wait.h>
#include <ctype.h>

//easyrsa configuration
char ERSA_DIR[]="/opt/easyrsa";
char TA_KEY[]="/opt/easyrsa/clients/ta.key";
char OUTPUT_DIR[]="/opt/easyrsa/clients";
char BASE_CONFIG[]="/opt/easyrsa/clients/base.conf";
char EXT[]=".ovpn";

//void printCN(char*,int);
void filePrint(char*);
void revokeCN(char*,int);
void createCN(char*,int);
void integrateCN(char*);
void getHelp(char*,int);
void cleanStr(char*);

//deprecated function - prints the CN ovpn config file
//conf file can be printed with inegrateCN(); <- create
void printCN(char *cn, int i){
	char fn[100];
	char buffer[100];

	if(i==1){
		printf("print->CN=");
		fflush(stdout);
		memset(buffer,0,sizeof(buffer));
		read(0,buffer,sizeof(buffer));
	} 
	else { 
		memset(buffer,0,sizeof(buffer));
		strncat(buffer,cn,sizeof(buffer)); 
	}

	if(!strncmp("\n",buffer,1)) { return; }

	do{
		strncpy(fn, OUTPUT_DIR,sizeof(fn));
		strncat(fn, "/",sizeof(fn)-strlen(fn));
		strncat(fn, strtok(basename(buffer),"\n"),sizeof(fn)-strlen(fn));
		strncat(fn, EXT, sizeof(fn)-strlen(fn));
		printf(buffer); //checking buffer content
		filePrint(fn);
		if(i==1){

			printf("\nprint->CN=");
			fflush(stdout);
			memset(buffer,0,sizeof(buffer));
			read(0,buffer,sizeof(buffer));
		}
	} while (strncmp("\n",buffer,1) && i==1);
}

void filePrint(char *filename){
	int bfsiz=1;
	char buffer[bfsiz];
	int fd;
	ssize_t fr;
	memset(buffer,0,bfsiz);
	setuid(0); //escalating privileges to read root owned files
	if((fd=open(filename,O_RDONLY))<0){
		printf("[!] ERR reading %s!\n",filename);
	}
	while(fr=read(fd,buffer,bfsiz)>0){
		printf("%s",buffer);
		memset(buffer,0,bfsiz);
	}
	close(fd);
	fflush(stdout);
}

void revokeCN(char *cn, int i){
	puts("[!] Not implemented");
	fflush(stdout);
}

//creates and prints new CN config file
void createCN(char *cn, int i){
	int devNull, sout, serr, pid, status, oid;
	char EASYRSA[50];
	char buffer[100];
	char CMD[100];
	char WD[50];
	
	memset(EASYRSA,0,sizeof(EASYRSA));
	strcat(EASYRSA,ERSA_DIR);
	strcat(EASYRSA,"/easyrsa");

	if(i==1){
		printf("create->CN=");
		fflush(stdout);
		memset(buffer,0,sizeof(buffer));
		read(0,buffer,sizeof(buffer));
	} 
	else { 
		memset(buffer,0,sizeof(buffer));
		strncat(buffer, cn, sizeof(buffer));
	}

	if(!strncmp("\n",buffer,1)) { return; }

	do{
		pid = vfork();
		if(pid==0){
			char *a[] = {EASYRSA,"build-client-full",strtok(basename(buffer),"\n"),"nopass","batch"};
			//forge the command string
			cleanStr(a[2]);
			sprintf(CMD,"%s %s %.20s %s %s",a[0],a[1],a[2],a[3],a[4]);
			sout=dup(STDOUT_FILENO);
			serr=dup(STDERR_FILENO);
			devNull=open("/dev/null",O_WRONLY);
			dup2(devNull,STDOUT_FILENO);
			dup2(devNull,STDERR_FILENO);
			setuid(0); //escalating privilges to generate required files
			chdir(ERSA_DIR);
			system(CMD);
			exit(0);
		} 
		dup2(sout,STDOUT_FILENO);
		dup2(serr,STDERR_FILENO);
		close(devNull);
		usleep(500000);
		integrateCN(buffer);

		if(i==1){
			printf("create->CN=");
			fflush(stdout);
			memset(buffer,0,sizeof(buffer));
			read(0,buffer,sizeof(buffer));
		}
	} while (strncmp("\n",buffer,1) && i==1);
}

//print valid ovpnfile for provided cn
void integrateCN(char *cn){
	char PKI_DIR[50];
	char KEY_DIR[50];
	char CRT_DIR[50];
	char CA_CERT[50];
	char CN_CERT[50];
	char CN_KEY[50];

	memset(PKI_DIR,0,sizeof(PKI_DIR));
	memset(KEY_DIR,0,sizeof(KEY_DIR));
	memset(CRT_DIR,0,sizeof(CRT_DIR));
	memset(CA_CERT,0,sizeof(CA_CERT));
	memset(CN_CERT,0,sizeof(CN_CERT));
	memset(CN_KEY,0,sizeof(CN_KEY));

	strcat(PKI_DIR,ERSA_DIR);
	strcat(PKI_DIR,"/pki");
	strcat(KEY_DIR,PKI_DIR);
	strcat(KEY_DIR,"/private");
	strcat(CRT_DIR,PKI_DIR);
	strcat(CRT_DIR,"/issued");
	strcat(CA_CERT,PKI_DIR);
	strcat(CA_CERT,"/ca.crt");
	strcat(CN_CERT,CRT_DIR);
	strcat(CN_CERT,"/");
	strcat(CN_CERT,basename(cn));
	strcat(CN_CERT,".crt");
	strcat(CN_KEY,KEY_DIR);
	strcat(CN_KEY,"/");
	strcat(CN_KEY,basename(cn));
	strcat(CN_KEY,".key");

	filePrint(BASE_CONFIG);

	printf("<ca>\n");
	filePrint(CA_CERT);
	printf("</ca>\n");
	
	printf("<cert>\n");
	filePrint(CN_CERT);
	printf("</cert>\n");

	printf("<key>\n");
	filePrint(CN_KEY);
	printf("</key>\n");

	printf("key-direction 1\n<tls-auth>\n");
	filePrint(TA_KEY);
	printf("</tls-auth>\n");
	fflush(stdout);
}

void getHelp(char *prog, int i){
	if(i==1) {
		printf("create|print|revoke|exit\n");
		fflush(stdout);
	}
	else{
		printf("batch mode: %s create|print|revoke CN\n",prog);
		fflush(stdout);
		exit(255);
	}
}

//clean non alphanum chars from string to secure
void cleanStr(char *str)
{
    unsigned long i = 0;
    unsigned long j = 0;
    char c;

    while ((c = str[i++]) != '\0')
    {
        if (isalnum(c))
        {
            str[j++] = c;
        }
    }
    str[j] = '\0';
}

int main(int argc, char **argv){
	int interactive=0;
	char opt[8];
	char *cn;

	if(argc!=3 && argc!=1){ 
		getHelp(argv[0],interactive);
	} 
	else if(argc==1){
		interactive=1;
		printf("# ");
		fflush(stdout);
		memset(opt,0,sizeof(opt));
		read(0,opt,sizeof(opt));
		cn=NULL;
	}
	else {
		strncpy(opt,argv[1],sizeof(opt));
		cn=argv[2];
	}

	do 	{		
		if(!strncmp("revoke",opt,6)){
			revokeCN(cn,interactive);
		} 
		else if (!strncmp("print",opt,5)){
			printCN(cn,interactive);
		}
		else if (!strncmp("create",opt,6)){
			createCN(cn,interactive);
		}
		else if (!strncmp("exit",opt,4)){
			exit(0);
		}
		else{ 
			getHelp(argv[0], interactive);
		}

		if(interactive==1){
			memset(opt,0,sizeof(opt));
			printf("# ");
			fflush(stdout);
			memset(opt,0,sizeof(opt));
			read(0,opt,sizeof(opt));
		}
	} while(interactive==1);
}

