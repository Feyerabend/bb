
## Prerequisites

- Python 3.x installed on your system
- The `hashlib` and `time` modules (these come built-in with Python)


## How to Run

1. *Run from command line/terminal*:
   ```bash
   python block.py
   ```
   or
   ```bash
   python3 block.py
   ```

2. *Run from Python interpreter*: You can also run it interactively by opening a Python
interpreter and pasting the code, or importing the file if saved.


## What It Does

When you run this code, it will:

1. Create a new blockchain with a genesis block (the first block)
2. Add two transaction blocks to the chain
3. Print out all blocks in the chain, showing:
   - Block index
   - Timestamp
   - Transaction data
   - Previous block's hash
   - Current block's hash
4. Validate that the blockchain is intact and hasn't been tampered with


## Expected Output

You'll see output similar to this:

```
Index: 0
Timestamp: 1671234567.123456
Data: Genesis Block
Previous Hash: 0
Hash: a1b2c3d4e5f6...

Index: 1
Timestamp: 1671234567.234567
Data: Transaction 1: Alice pays Bob 5 BTC
Previous Hash: a1b2c3d4e5f6...
Hash: b2c3d4e5f6a1...

Index: 2
Timestamp: 1671234567.345678
Data: Transaction 2: Bob pays Charlie 2 BTC
Previous Hash: b2c3d4e5f6a1...
Hash: c3d4e5f6a1b2...

Blockchain valid: True
```

The timestamps and hashes will be different each time you run it
since they're generated based on the current time.

