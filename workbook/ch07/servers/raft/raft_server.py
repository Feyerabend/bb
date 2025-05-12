import random
import time
from raft_database import RaftDatabase

class RaftServer:
    def __init__(self, id, db):
        self.id = id
        self.state = "FOLLOWER"
        self.db = db
        self.current_term = 0
        self.voted_for = None

    def start_election(self):
        print(f"[ELECTION] Server {self.id} starting election for term {self.current_term + 1}")
        self.state = "CANDIDATE"
        self.current_term += 1
        self.db.append_log(self.current_term, f"Election started by server {self.id}")

        # simulate vote gathering
        election_timeout = random.uniform(1, 3)  # random timeout between 1 and 3 seconds (in actual case hundreds of ms)
        time.sleep(election_timeout)  # simulate a random election timeout
        if random.choice([True, False]):
            print(f"[ELECTION] Server {self.id} wins election for term {self.current_term}")
            self.state = "LEADER"
            self.db.append_log(self.current_term, f"Leader elected: server {self.id}")
        else:
            self.state = "FOLLOWER"

    def process_command(self, command):
        if self.state == "LEADER":
            print(f"[LEADER] Server {self.id} processing command: {command}")
            key, value = command.split("=", 1)
            self.db.update_db(key.strip(), value.strip())  # update DB with new value
            self.db.append_log(self.current_term, f"Updated DB: {key.strip()} = {value.strip()}")
        else:
            print(f"[FOLLOWER] Server {self.id} forwarding command: {command}")
