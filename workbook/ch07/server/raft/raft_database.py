import os
import json

class RaftDatabase:
    def __init__(self, db_file="raft_db.json", log_file="raft_log.json"):
        self.db_file = db_file
        self.log_file = log_file
        self.load_db()
        self.load_log()

    def load_db(self):
        if os.path.exists(self.db_file):
            with open(self.db_file, 'r') as f:
                self.db = json.load(f)
        else:
            self.db = {"counter": 0}  # data: simple counter to be incremented

    def save_db(self):
        with open(self.db_file, 'w') as f:
            json.dump(self.db, f)

    def load_log(self):
        if os.path.exists(self.log_file):
            with open(self.log_file, 'r') as f:
                self.log = json.load(f)
        else:
            self.log = []

    def append_log(self, term, command):
        log_entry = {
            "term": term,
            "command": command
        }
        self.log.append(log_entry)
        self.save_log()

    def save_log(self):
        with open(self.log_file, 'w') as f:
            json.dump(self.log, f)

    def get_log(self):
        return self.log

    def get_current_term(self):
        if self.log:
            return self.log[-1]["term"]
        return 0  # no entries yet

    def set_voted_for(self, server_id):
        self.voted_for = server_id

    def get_db_state(self):
        return self.db

    def update_db(self, key, value):
        self.db[key] = value
        self.save_db()
