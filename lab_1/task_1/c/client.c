#include <netdb.h>
#include <netinet/in.h>
#include <stdio.h>
#include <sys/socket.h>
#include <sys/types.h>

#define DATA "The sea is calm, the tide is full . . ."
#define ALPHABET "abcdefghijklmnopqrstuvwxyz"
#define DATA_GRAM_LENGTH 60
#define DATA_GRAM_NUMBER 10

struct arguments {
    struct hostent *host_address;
    u_int16_t port;
};

typedef struct arguments Arguments;

void get_random_string(char *buffer, size_t buffer_length) {
    static char charset[] = ALPHABET;
    if (buffer_length) {
        if (buffer) {
            for (int n = 0; n < buffer_length; ++n) {
                int key = rand() % (int)(sizeof(charset) - 1);
                buffer[n] = charset[key];
            }
        }
    }
}

void parse_arguments(int argc, char *argv[], Arguments *arguments) {
    char *host;
    u_int16_t port;

    if (argc < 3) {
        host = "localhost";
        port = 8000;
    } else {
        host = argv[1];
        port = htons(atoi(argv[2]));
    }

    struct hostent *host_info;
    host_info = gethostbyname(host);

    if (host_info == (struct hostent *)0) {
        fprintf(stderr, "%s: unknown host\n", host);
        exit(2);
    }

    arguments->host_address = host_info;
    arguments->port = port;
}

int main(int argc, char *argv[]) {
    int sock;
    struct sockaddr_in name;
    Arguments arguments;

    parse_arguments(argc, argv, &arguments);

    sock = socket(AF_INET, SOCK_DGRAM, 0);
    if (sock == -1) {
        perror("opening datagram socket");
        exit(1);
    }

    memcpy((char *)&name.sin_addr, (char *)arguments.host_address->h_addr,
           arguments.host_address->h_length);

    name.sin_family = AF_INET;
    name.sin_port = arguments.port;

    if (connect(sock, (struct sockaddr *)&name, sizeof name) == -1) {
        perror("Connect");
        exit(3);
    }

    char buffer[DATA_GRAM_LENGTH + 1];
    buffer[DATA_GRAM_LENGTH] = '\0';

    for (u_int8_t i = 0; i < DATA_GRAM_NUMBER; ++i) {
        get_random_string(buffer, DATA_GRAM_LENGTH);
        printf("Sending %s", buffer);

        if (send(sock, buffer, DATA_GRAM_LENGTH, 0) == -1) {
            perror("sending datagram message");
            exit(4);
        }
    }

    printf("6\n");

    close(sock);
    exit(0);
}
