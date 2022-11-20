#include <netinet/in.h>
#include <stdio.h>
#include <sys/socket.h>
#include <sys/types.h>

#define WORK 1
#define BUFSIZE 1024

void main(void) {
    int sock, length;
    struct sockaddr_in name;
    char buf[BUFSIZE + 1];
    buf[BUFSIZE] = '\0';

    sock = socket(AF_INET, SOCK_DGRAM, 0);
    if (sock == -1) {
        perror("opening datagram socket");
        exit(1);
    }

    /* Create name with wildcards. */
    name.sin_family = AF_INET;
    name.sin_addr.s_addr = INADDR_ANY;
    name.sin_port = 0;  // TODO: Do it better

    if (bind(sock, (struct sockaddr *)&name, sizeof name) == -1) {
        perror("binding datagram socket");
        exit(1);
    }

    /* Wydrukuj na konsoli numer portu */
    length = sizeof(name);

    if (getsockname(sock, (struct sockaddr *)&name, &length) == -1) {
        perror("getting socket name");
        exit(1);
    }

    printf("Socket port: %d\n", ntohs(name.sin_port));

    while (WORK) {
        /* Read from the socket. */
        int bytes_read = read(sock, buf, BUFSIZE);

        if (bytes_read == -1) {
            perror("receiving datagram packet");
            exit(2);
        }
        buf[bytes_read] = '\0';

        printf("-->%s\n", buf);
    }

    close(sock);
    exit(0);
}