import logging # use built-in logging module
import time

class Server:
    def __init__(self, name):
        self.name = name
        self.setup_logging()

    def setup_logging(self):
        logging.basicConfig(filename=f"{self.name}_tasks.log", level=logging.INFO)

    def process_task(self, task):
        start_time = time.time()
        logging.info(f"Starting task: {task} at {time.ctime(start_time)}")
        
        # simulate task processing time
        time.sleep(2)  # simulate task processing time
        
        end_time = time.time()
        duration = end_time - start_time
        logging.info(f"Completed task: {task} at {time.ctime(end_time)}. Duration: {duration:.2f} seconds")
        print(f"Server {self.name} completed task: {task}")

def main():
    server = Server(name="ServerOne")
    
    # simulate tasks being processed
    tasks = ["Task 1", "Task 2", "Task 3"]
    
    for task in tasks:
        server.process_task(task)
        time.sleep(1)

if __name__ == "__main__":
    main()
