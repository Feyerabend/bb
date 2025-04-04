import random
import threading
import time

class Server:
    def __init__(self, name):
        self.name = name

    def process_task(self, task):
        print(f"Server {self.name} starting task: {task}")
        if random.choice([True, False]):  # simulate random failure
            print(f"Server {self.name} failed to process task: {task}")
            return False
        time.sleep(1)  # simulate task processing time
        print(f"Server {self.name} successfully completed task: {task}")
        return True

    def handle_task(self, task):
        retries = 3
        for _ in range(retries):
            if self.process_task(task):
                return
            print(f"Retrying task {task}...")
            time.sleep(1)
        print(f"Server {self.name} gave up on task: {task}")

def main():
    server = Server(name="Server 1")
    
    # Simulate tasks being processed
    tasks = ["Task 1", "Task 2", "Task 3"]
    
    for task in tasks:
        threading.Thread(target=server.handle_task, args=(task,), daemon=True).start()
        time.sleep(0.5)  # simulate time between tasks

    time.sleep(10)  # let servers finish their tasks

if __name__ == "__main__":
    main()
