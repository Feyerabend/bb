import csv
import random

# Simulated database storing names from CSV and random phone numbers.
class NameDatabase:
    def __init__(self, csv_file='names.csv'):
        self.database = {}
        try:
            with open(csv_file, 'r', encoding='utf-8') as file:
                csv_reader = csv.DictReader(file)
                for row in csv_reader:
                    girl_name = row.get('Girl Name', '').strip()
                    boy_name = row.get('Boy Name', '').strip()
                    
                    if girl_name:
                        self.database[girl_name] = f"555-{random.randint(100, 999)}-{random.randint(1000, 9999)}"
                    if boy_name:
                        self.database[boy_name] = f"555-{random.randint(100, 999)}-{random.randint(1000, 9999)}"
        except FileNotFoundError:
            raise FileNotFoundError(f"Error: File '{csv_file}' not found.")
        except Exception as e:
            raise Exception(f"Error reading CSV file: {e}")
    
    def get_phone_by_name(self, name):
        return self.database.get(name, None)
    
    def get_all_names(self):
        return [(name, phone) for name, phone in self.database.items()]
    
