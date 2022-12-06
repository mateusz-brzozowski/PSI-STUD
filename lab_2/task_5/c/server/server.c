// Laboratorium 2 Zadanie 2.5 Serwer w C
// Autorzy: Mateusz Brzozowski, Bartłomiej Krawczyk, Jakub Marcowski, Aleksandra Sypuła
// Data ukończenia: 06.12.2022

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
#define BUFSIZE 10

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
        if (port = atoi(argv[1]))
            port = htons(port);
        else {
            perror("Error, not able to parse provided arguments.");
            exit(1);
        }
    }

    printf("Will listen on 0.0.0.0:%d\n", ntohs(port));
    fflush(stdout);

    return port;
}

void receive_message(int socket_file_descriptor) {
    struct sockaddr_in client_address;
    socklen_t client_address_length = sizeof client_address;
    char buffer[BUFSIZE + 1];
    int max_message_buffer_size = 100000;
    char message_buffer[max_message_buffer_size + 1];
    char *client_address_string;
    int message_socket_file_descriptor;
    int bytes_read;
    int already_read = 0;

    buffer[BUFSIZE] = '\0';
    memset(&message_buffer, 0, max_message_buffer_size);
    memset(&client_address, 0, client_address_length);

    message_socket_file_descriptor =
        accept(socket_file_descriptor, (struct sockaddr *)&client_address, &client_address_length);
    if (message_socket_file_descriptor == -1) {
        perror("accept");
        exit(4);
    }

    client_address_string = inet_ntoa(client_address.sin_addr);
    if (client_address_string != 0) {
        printf("Client address: %s:%d\n", client_address_string, ntohs(client_address.sin_port));
    }

    do {
        bytes_read = recv(message_socket_file_descriptor, buffer, BUFSIZE, 0);
        if (bytes_read == -1) {
            perror("Exception while receiving stream packet");
        } else {
            buffer[bytes_read] = '\0';

            if (already_read + bytes_read > max_message_buffer_size) {
                printf("Didn't expect such a long message!");
                printf("Part of long message: %s", message_buffer);
                memset(&message_buffer, 0, max_message_buffer_size);
                already_read = 0;
            }
            memcpy(message_buffer + already_read, buffer, bytes_read + 1);
            already_read += bytes_read;

            printf("%s\n", buffer);

            fflush(stdout);
        }
    } while (bytes_read > 0);

    printf("Message received: %s\n", message_buffer);

    close(message_socket_file_descriptor);
}

/* makes use of fork() and wait() to handle multiple clients
prints out what thread the message was received on */
void receive_message_concurrent(int socket_file_descriptor) {
    struct sockaddr_in client_address;
    socklen_t client_address_length = sizeof client_address;
    char buffer[BUFSIZE + 1];
    char *client_address_string;
    int message_socket_file_descriptor;
    int bytes_read;
    int pid;

    buffer[BUFSIZE] = '\0';
    memset(&client_address, 0, client_address_length);

    message_socket_file_descriptor =
        accept(socket_file_descriptor, (struct sockaddr *)&client_address, &client_address_length);
    if (message_socket_file_descriptor == -1) {
        perror("accept");
        exit(4);
    }

    client_address_string = inet_ntoa(client_address.sin_addr);
    if (client_address_string != 0) {
        printf("Client address: %s:%d\n", client_address_string, ntohs(client_address.sin_port));
    }

    pid = fork();
    if (pid == 0) {
        do {
            bytes_read = recv(message_socket_file_descriptor, buffer, BUFSIZE, 0);
            if (bytes_read == -1) {
                perror("Exception while receiving stream packet");
            } else {
                buffer[bytes_read] = '\0';
                printf("Thread %d: %s\n", getpid(), buffer);
                fflush(stdout);
            }
        } while (bytes_read > 0);

        close(message_socket_file_descriptor);
        exit(0);
    } else {
        close(message_socket_file_descriptor);
    }
}

int main(int argc, char *argv[]) {
    int socket_file_descriptor;
    struct sockaddr_in server_address;

    if ((socket_file_descriptor = socket(AF_INET, SOCK_STREAM, 0)) == -1) {
        perror("Error while opening stream socket");
        exit(2);
    }

    memset(&server_address, '\0', sizeof(server_address));

    server_address.sin_family = AF_INET;
    server_address.sin_addr.s_addr = INADDR_ANY;
    server_address.sin_port = parse_argument(argc, argv);

    if (bind(socket_file_descriptor, (struct sockaddr *)&server_address, sizeof(server_address)) == -1) {
        perror("binding stream socket");
        exit(3);
    }

    listen(socket_file_descriptor, 10);

    while (WORK) {
        // receive_message(socket_file_descriptor);
        receive_message_concurrent(socket_file_descriptor);
    }

    close(socket_file_descriptor);

    return 0;
}
