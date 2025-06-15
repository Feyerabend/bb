
## Prerequisites

First, you'll need to install the required dependencies:

```bash
pip install flask ecdsa requests waitress
```

(Recommended to run in a virtual environment.)


## Basic Usage

### 1. Running a Single Node (Development Mode)

Run:

```bash
python coins.py
```

This will start a development server on `http://localhost:5000` with:
- Default mining difficulty of 4
- Mining reward of 10.0 coins
- Test transactions and wallets automatically created
- Debug logging enabled


### 2. Custom Configuration

You can customize the blockchain parameters:

```bash
# Custom port
python coins.py --port 5001

# Custom mining difficulty (higher = more difficult)
python coins.py --difficulty 6

# Custom mining reward
python coins.py --reward 25.0

# Production mode (requires waitress)
python coins.py --production --port 8080
```


### 3. Running Multiple Nodes (Network Simulation)

To simulate a blockchain network, run multiple nodes on different ports:

```bash
# Terminal 1
python coins.py --port 5000

# Terminal 2
python coins.py --port 5001

# Terminal 3
python coins.py --port 5002
```


## API Endpoints

Once running, you can interact with the blockchain via HTTP requests:

### View the Blockchain
```bash
curl http://localhost:5000/chain
```

### Create a Transaction
```bash
curl -X POST http://localhost:5000/transaction/new \
  -H "Content-Type: application/json" \
  -d '{
    "sender": "sender_public_key",
    "recipient": "recipient_public_key", 
    "amount": 10.0,
    "signature": "base64_encoded_signature"
  }'
```

### Mine Pending Transactions
```bash
curl -X POST http://localhost:5000/mine \
  -H "Content-Type: application/json" \
  -d '{"miner_address": "miner_public_key"}'
```

### Check Account Balance
```bash
curl http://localhost:5000/balance/your_wallet_address
```

### Register Network Nodes
```bash
curl -X POST http://localhost:5000/nodes/register \
  -H "Content-Type: application/json" \
  -d '{"nodes": ["http://localhost:5001", "http://localhost:5002"]}'
```

### Resolve Chain Conflicts (Consensus)
```bash
curl http://localhost:5000/nodes/resolve
```

## What Happens When You Run It

1. *Initialisation*: Creates a genesis block and sets up the blockchain
2. *Test Data* (development mode only): 
   - Creates test wallets for Alice, Bob, and a miner
   - Adds sample transactions
   - Mines a test block
   - Displays balances in the logs
3. *Persistence*: Automatically saves blockchain state to `coin_blockchain.dat`
4. *API Server*: Starts Flask server with all endpoints available


## Key Features

- *Digital Signatures*: Transactions are cryptographically signed using ECDSA
- *Proof of Work*: Mining requires solving computational puzzles
- *Network Consensus*: Multiple nodes can sync and resolve conflicts
- *Persistence*: Blockchain state is saved to disk
- *REST API*: Full HTTP API for all operations
- *Validation*: Complete transaction and block validation
- *Observer Pattern*: Automatic broadcasting to network nodes


## Production Deployment

For production use:

```bash
pip install waitress
python coins.py --production --port 8080 --difficulty 6
```

This uses the Waitress WSGI server instead of Flask's development server.

## Troubleshooting

- *Port already in use*: Change the port with `--port XXXX`
- *Import errors*: Make sure all dependencies are installed
- *Network issues*: Check firewall settings for node communication
- *Mining too slow*: Reduce difficulty with `--difficulty 2`

The blockchain will automatically create wallets, process transactions,
and maintain consensus across the network once you have it running.


