#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <netinet/in.h>

#define PORT 8080
#define RESPONSE "HTTP/1.0 200 OK\r\n" \
                 "Content-Type: text/plain\r\n" \
                 "Content-Length: 13\r\n\r\n" \
                 "Hello, World!"

// Compile with: gcc -o server server.c
// Run with: ./server
// Access with: curl http://localhost:8080
// works on Linux and MacOS
int main() {
    int server_fd, client_fd;
    struct sockaddr_in address;
    socklen_t addrlen = sizeof(address);
    char buffer[1024] = {0};

    // create socket
    server_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (server_fd == -1) {
        perror("socket");
        exit(1);
    }

    // bind to port
    address.sin_family = AF_INET;
    address.sin_addr.s_addr = INADDR_ANY;
    address.sin_port = htons(PORT);

    if (bind(server_fd, (struct sockaddr*)&address, sizeof(address)) < 0) {
        perror("bind");
        close(server_fd);
        exit(1);
    }

    // listen
    if (listen(server_fd, 5) < 0) {
        perror("listen");
        close(server_fd);
        exit(1);
    }

    printf("Server listening on http://localhost:%d\n", PORT);

    while (1) {
        // accept
        client_fd = accept(server_fd, (struct sockaddr*)&address, &addrlen);
        if (client_fd < 0) {
            perror("accept");
            continue;
        }

        // read request (we discard it)
        read(client_fd, buffer, sizeof(buffer) - 1);

        // send fixed response
        write(client_fd, RESPONSE, strlen(RESPONSE));
        close(client_fd);
    }

    close(server_fd);
    return 0;
}
