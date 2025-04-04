import time
import random
from raft_server import RaftServer
from raft_database import RaftDatabase

def simulate_cluster():
    # persistent database and servers (server IDs: 1, 2, 3)
    db = RaftDatabase()
    servers = [RaftServer(i, db) for i in range(1, 4)]

    # link servers together
    for server in servers:
        server.servers = [s for s in servers if s != server]  # each server knows of the others

    # simulate a running cluster
    try:
        while True:
            # randomly trigger an election
            random.choice(servers).start_election()

            # simulate client commands (appending data to logs and updating DB)
            leader = next((s for s in servers if s.state == "LEADER"), None)
            if leader:
                command = f"counter = {random.randint(1, 100)}"
                print(f"\n[CLIENT] Sending command: {command}")
                leader.process_command(command)

            print(f"\n[DB STATE] Current database state: {db.get_db_state()}")

            time.sleep(5)
    except KeyboardInterrupt: # interrupt with CTRL-C (or corresponding)
        print("Stopping servers...")

if __name__ == "__main__":
    simulate_cluster()
