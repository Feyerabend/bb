import time

class Server:
    def __init__(self, name):
        self.name = name
        self.cache = {}

    def process_task(self, task):
        if task in self.cache:
            print(f"Server {self.name} returning cached result for {task}")
            return self.cache[task]
        else:
            print(f"Server {self.name} processing task: {task}")
            result = f"Processed {task}"  # simulate a complex task
            time.sleep(2)  # simulate task processing time
            self.cache[task] = result
            return result

def main():
    server = Server(name="Server 1")
    
    # simulate tasks being processed
    tasks = ["Task 1", "Task 2", "Task 1", "Task 3", "Task 2"]
    
    for task in tasks:
        result = server.process_task(task)
        print(f"Result: {result}")
        time.sleep(1)

if __name__ == "__main__":
    main()
