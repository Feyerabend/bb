
import re
from procedures import DatabaseProcedures

class SimpleInterpreter:
    def __init__(self, db):
        self.db = db

    def execute(self, command):

        add_pattern = re.compile(r"add (\w+) (.+)")
        delete_pattern = re.compile(r"delete (\w+)")
        increment_pattern = re.compile(r"increment (\w+) (\d+)")
        
        if match := add_pattern.match(command):
            key, value = match.groups()
            self.db.add(key, value)
            return f"Added {key}: {value}"

        elif match := delete_pattern.match(command):
            key, = match.groups()
            self.db.delete(key)
            return f"Deleted {key}"

        elif match := increment_pattern.match(command):
            key, amount = match.groups()
            DatabaseProcedures.increment_value(self.db, key, int(amount))
            return f"Incremented {key} by {amount}"

        return "Invalid command"
