#include <errno.h>
#include <netinet/in.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/types.h>

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

    return port;
}

void main(int argc, char *argv[]) {
    int socket_file_descriptor, length;
    struct sockaddr_in server_address;
    struct sockaddr_in client_address;
    char buf[BUFSIZE + 1];

    buf[BUFSIZE] = '\0';

    socket_file_descriptor = socket(AF_INET, SOCK_DGRAM, 0);
    if (socket_file_descriptor == -1) {
        perror("opening datagram socket");
        exit(1);
    }

    server_address.sin_family = AF_INET;
    server_address.sin_addr.s_addr = htonl(INADDR_ANY);
    server_address.sin_port = parse_argument(argc, argv);

    if (bind(socket_file_descriptor, (struct sockaddr *)&server_address, sizeof(server_address)) == -1) {
        perror("binding datagram socket");
        exit(1);
    }

    length = sizeof(server_address);

    printf("Socket port: %d\n", ntohs(server_address.sin_port));
    memset(&client_address, 0, sizeof(client_address));

    while (WORK) {
        printf("Set client addres to 0\n");
        int bytes_read = recvfrom(socket_file_descriptor, buf, BUFSIZE, MSG_WAITALL,
                                  (const struct sockaddr *)&client_address, sizeof(client_address));
        printf("-->%s\n", buf);
        printf("Printf %d", errno);

        if (bytes_read == -1) {
            printf("Printf %d", errno);
            perror("receiving datagram packet");
            printf("Printf %d", errno);
            exit(2);
        } else {
            printf("Bytes read: %d", bytes_read);
        }
        buf[bytes_read] = '\0';

        printf("-->%s\n", buf);
        printf("Client address: %s:%s", ntohl(client_address.sin_addr.s_addr), ntohs(client_address.sin_port));
    }

    close(socket_file_descriptor);
    exit(0);
}