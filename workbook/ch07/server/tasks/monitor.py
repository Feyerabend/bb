import threading
import time

class Server:
    def __init__(self, name):
        self.name = name
        self.health = True  # = healthy

    def perform_health_check(self):
        while True:
            if self.health:
                print(f"Server {self.name} is healthy.")
            else:
                print(f"Server {self.name} has a problem!")
            time.sleep(5)  # health check every 5 seconds

    def simulate_failure(self):
        print(f"Server {self.name} encountered a failure.")
        self.health = False
        time.sleep(3)
        self.health = True  # server recovers after 3 seconds

def main():
    server = Server(name="Server 1")
    
    # start health check thread
    threading.Thread(target=server.perform_health_check, daemon=True).start()

    # simulate a server failure and recovery
    time.sleep(3)
    threading.Thread(target=server.simulate_failure, daemon=True).start()

    # allow the server to perform health checks
    time.sleep(15)

if __name__ == "__main__":
    main()
