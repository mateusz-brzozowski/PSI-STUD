#include <arpa/inet.h>
#include <errno.h>
#include <netinet/in.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <unistd.h>

#define WORK 1
#define BUFSIZE 1024

struct arguments {
    struct hostent *host_address;
    u_int16_t port;
};

typedef struct arguments Arguments;

int parse_argument(int argc, char *argv[]) {
    u_int16_t port;

    if (argc < 2) {
        port = htons(8000);
    } else {
        port = htons(atoi(argv[1]));
    }

    printf("Will listen on 0.0.0.0:%d\n", ntohs(port));
    fflush(stdout);

    return port;
}

int main(int argc, char *argv[]) {
    int socket_file_descriptor;
    struct sockaddr_in server_address;
    struct sockaddr_in client_address;
    char buffer[BUFSIZE + 1];
    socklen_t client_address_length = sizeof client_address;
    char *client_address_string;

    buffer[BUFSIZE] = '\0';

    if ((socket_file_descriptor = socket(AF_INET, SOCK_DGRAM, 0)) == -1) {
        perror("opening datagram socket");
        exit(1);
    }

    memset(&server_address, '\0', sizeof(server_address));
    server_address.sin_family = AF_INET;
    server_address.sin_addr.s_addr = INADDR_ANY;
    server_address.sin_port = parse_argument(argc, argv);

    if (bind(socket_file_descriptor, (struct sockaddr *)&server_address, sizeof(server_address)) == -1) {
        perror("binding datagram socket");
        exit(2);
    }

    memset(&client_address, 0, client_address_length);

    while (WORK) {
        memset(&client_address, 0, client_address_length);

        int bytes_read = recvfrom(socket_file_descriptor, buffer, BUFSIZE, 0, (struct sockaddr *)&client_address,
                                  &client_address_length);

        if (bytes_read == -1) {
            perror("Exception while receiving datagram packet");
        } else {
            buffer[bytes_read] = '\0';

            printf("Message received: %s\n", buffer);
            client_address_string = inet_ntoa(client_address.sin_addr);
            if (client_address_string != 0) {
                printf("Client address: %s:%d\n", client_address_string, ntohs(client_address.sin_port));
            }
            fflush(stdout);
        }
    }

    close(socket_file_descriptor);
    return 0;
}