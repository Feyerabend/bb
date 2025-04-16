import queue
import threading
import time

class Server:
    def __init__(self, name, weight=1):
        self.name = name
        self.weight = weight
        self.tasks = queue.Queue()

    def process_task(self, task_status):
        while True:
            task, task_id = self.tasks.get()
            if task is None:  # sentinel value (stop signal) to stop the thread
                break
            print(f"Server {self.name} is processing task: {task}")
            task_status[task_id]['started'] = True  # task as started
            time.sleep(2)  # simulate task processing time
            task_status[task_id]['completed'] = True  # mark the task as completed
            print(f"Server {self.name} completed task: {task}")

    def add_task(self, task, task_id):
        self.tasks.put((task, task_id))

class WeightedLoadBalancer:
    def __init__(self, servers):
        self.servers = servers
        self.total_weight = sum(server.weight for server in servers)
        self.server_index = 0

    def distribute_task(self, task, task_id, task_status):
        # weighted round-robin approach
        weight_sum = 0
        selected_server = None
        for server in self.servers:
            weight_sum += server.weight
            if weight_sum >= self.server_index:
                selected_server = server
                break

        print(f"Distributing {task} to {selected_server.name} with weight {selected_server.weight}")
        selected_server.add_task(task, task_id)
        
        self.server_index = (self.server_index + 1) % self.total_weight

    def check_task_status(self, task_status):
        all_started = all(status['started'] for status in task_status.values())
        all_completed = all(status['completed'] for status in task_status.values())
        
        if all_started:
            print("All tasks have been started.")
        else:
            print("Not all tasks have been started.")
        
        if all_completed:
            print("All tasks have been completed.")
        else:
            print("Not all tasks have been completed.")
        
        return all_started, all_completed

def main():
    servers = [Server(name=f"Server {i+1}", weight=(i+1)) for i in range(3)]
    load_balancer = WeightedLoadBalancer(servers)

    task_status = {}

    for server in servers:
        threading.Thread(target=server.process_task, args=(task_status,), daemon=True).start()

    tasks = ["Task 1", "Task 2", "Task 3", "Task 4", "Task 5", "Task 6", "Task 7"]
    
    for task_id, task in enumerate(tasks):
        print(f"Distributing {task}")
        task_status[task_id] = {'started': False, 'completed': False}
        load_balancer.distribute_task(task, task_id, task_status)
        time.sleep(1)

    # wait, let servers finish
    time.sleep(15)

    load_balancer.check_task_status(task_status)

if __name__ == "__main__":
    main()
