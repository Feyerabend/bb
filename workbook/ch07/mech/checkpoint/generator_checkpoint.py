# generator_checkpoint.py

import json

CHECKPOINT_FILE = 'checkpoint.json'
DATA_FILE = 'numbers.txt'

def number_stream(filename, start_offset):
    with open(filename, 'r') as f:
        f.seek(start_offset)
        while line := f.readline():
            yield f.tell(), int(line.strip())

def load_checkpoint():
    try:
        with open(CHECKPOINT_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {'offset': 0, 'running_sum': 0}

def save_checkpoint(offset, running_sum):
    with open(CHECKPOINT_FILE, 'w') as f:
        json.dump({'offset': offset, 'running_sum': running_sum}, f)

def process():
    state = load_checkpoint()
    offset = state['offset']
    running_sum = state['running_sum']

    stream = number_stream(DATA_FILE, offset)
    pos = offset  # Initialize pos safely

    for pos, number in stream:
        running_sum += number
        if pos % 10000 < 50:
            save_checkpoint(pos, running_sum)

    save_checkpoint(pos, running_sum)
    print("Final sum:", running_sum)

if __name__ == '__main__':
    process()
