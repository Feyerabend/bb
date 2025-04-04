import queue
import threading
import time

class Server:
    def __init__(self, name):
        self.name = name
        self.tasks = queue.PriorityQueue()

    def process_task(self):
        while True:
            priority, task = self.tasks.get()
            if task is None:  # value to stop the thread
                break
            print(f"Server {self.name} is processing task: {task}")
            time.sleep(1)  # simulate task processing time
            print(f"Server {self.name} completed task: {task}")

    def add_task(self, task, priority):
        self.tasks.put((priority, task))

class PriorityTaskManager:
    def __init__(self, servers):
        self.servers = servers

    def distribute_task(self, task, priority):
        server = self.servers[0]  # example: distributing to first server
        print(f"Distributing {task} with priority {priority}")
        server.add_task(task, priority)

def main():
    servers = [Server(name=f"Server {i+1}") for i in range(2)]
    task_manager = PriorityTaskManager(servers)

    # start server threads
    for server in servers:
        threading.Thread(target=server.process_task, daemon=True).start()

    # simulate tasks being sent to the task manager
    tasks = [("Task 1", 2), ("Task 2", 1), ("Task 3", 3)]
    
    for task, priority in tasks:
        task_manager.distribute_task(task, priority)
        time.sleep(1)

    time.sleep(10)  # servers finish their tasks

if __name__ == "__main__":
    main()
