# checkpoint_stream.py

import json

CHECKPOINT_FILE = 'checkpoint.json'
DATA_FILE = 'numbers.txt'

def load_checkpoint():
    try:
        with open(CHECKPOINT_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {'offset': 0, 'running_sum': 0}

def save_checkpoint(offset, running_sum):
    with open(CHECKPOINT_FILE, 'w') as f:
        json.dump({'offset': offset, 'running_sum': running_sum}, f)

def process_stream():
    state = load_checkpoint()
    offset = state['offset']
    running_sum = state['running_sum']

    with open(DATA_FILE, 'r') as f:
        f.seek(offset)
        while line := f.readline():
            number = int(line.strip())
            running_sum += number
            # Save checkpoint every 1000 iterations
            if f.tell() % 1000 < len(line):  # crude modulo to avoid saving too often
                save_checkpoint(f.tell(), running_sum)
        # Final checkpoint at end
        save_checkpoint(f.tell(), running_sum)

    print("Final sum:", running_sum)

if __name__ == '__main__':
    process_stream()
