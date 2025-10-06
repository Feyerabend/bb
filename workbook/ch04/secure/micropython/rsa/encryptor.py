# RSA ENCRYPTOR
# Asymmetric encryption using RSA public key
# Wiring: UART TX (GP0) -> Pico2 RX, GND -> GND

import _thread
import time
from machine import UART, Pin
import urandom

# RSA Implementation
def gcd(a, b):
    while b:
        a, b = b, a % b
    return a

# Modular inverse using Extended Euclidean Algorithm
def mod_inverse(e, phi):
    def extended_gcd(a, b):
        if a == 0:
            return b, 0, 1
        gcd_val, x1, y1 = extended_gcd(b % a, a)
        x = y1 - (b // a) * x1
        y = x1
        return gcd_val, x, y
    
    _, x, _ = extended_gcd(e % phi, phi)
    return (x % phi + phi) % phi

# Miller-Rabin Primality Test
def is_prime(n, k=5):
    if n < 2:
        return False
    if n == 2 or n == 3:
        return True
    if n % 2 == 0:
        return False
    
    r, d = 0, n - 1
    while d % 2 == 0:
        r += 1
        d //= 2
    
    for _ in range(k):
        a = urandom.randint(2, n - 2)
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True

def generate_prime(bits=16):
    while True:
        n = urandom.getrandbits(bits)
        n |= (1 << bits - 1) | 1  # Set MSB and LSB
        if is_prime(n):
            return n

# Modular exponentiation (can work in parallel)
def pow_mod(base, exp, mod):
    result = 1
    base = base % mod
    while exp > 0:
        if exp % 2 == 1:
            result = (result * base) % mod
        exp = exp >> 1
        base = (base * base) % mod
    return result

# RSA key pair (pre-generated for demo, 32-bit keys for speed)
# In production, use proper key sizes (2048+ bits)
RSA_PUBLIC_KEY = {
    'n': 3233,      # p * q (53 * 61)
    'e': 17         # Public exponent
}

# Shared data structures
encrypt_queue = []
result_queue = []
core1_ready = False
lock = _thread.allocate_lock()

# Core 1: RSA encryption worker
def core1_task():
    global core1_ready
    print("[Core 1] RSA crypto engine started")
    core1_ready = True
    
    while True:
        if encrypt_queue:
            with lock:
                data = encrypt_queue.pop(0)
            
            msg_int, n, e = data
            
            # Perform RSA encryption: c = m^e mod n
            start = time.ticks_ms()
            encrypted = pow_mod(msg_int, e, n)
            duration = time.ticks_diff(time.ticks_ms(), start)
            
            with lock:
                result_queue.append((encrypted, duration))
            
            print(f"[Core 1] Encrypted block in {duration}ms")
        
        time.sleep_ms(5)

# RSA encrypt bytes (Core 0)
def rsa_encrypt_bytes(data, public_key):
    n = public_key['n']
    e = public_key['e']
    
    # Calculate max block size (must be < n)
    max_block_size = (n.bit_length() - 1) // 8
    
    encrypted_blocks = []
    
    # Split data into blocks
    for i in range(0, len(data), max_block_size):
        block = data[i:i + max_block_size]
        
        # Convert block to integer
        msg_int = int.from_bytes(block, 'big')
        
        if msg_int >= n:
            raise ValueError(f"Block too large: {msg_int} >= {n}")
        
        # Send to Core 1 for encryption
        with lock:
            encrypt_queue.append((msg_int, n, e))
        
        # Wait for result
        while True:
            with lock:
                if result_queue:
                    encrypted, duration = result_queue.pop(0)
                    break
            time.sleep_ms(5)
        
        # Store encrypted block with size
        encrypted_blocks.append(encrypted)
    
    return encrypted_blocks

def main():
    global core1_ready
    
    print("=" * 50)
    print("PICO 2 RSA ENCRYPTOR - Asymmetric Crypto")
    print("=" * 50)
    print(f"RSA Public Key (n={RSA_PUBLIC_KEY['n']}, e={RSA_PUBLIC_KEY['e']})")
    print(f"Key size: {RSA_PUBLIC_KEY['n'].bit_length()} bits")
    print("\nWiring:")
    print("  GP0 (UART TX) -> Pico2 RX")
    print("  GND -> GND")
    print("=" * 50)
    
    # Start Core 1 crypto engine
    _thread.start_new_thread(core1_task, ())
    
    while not core1_ready:
        time.sleep_ms(100)
    
    # Setup UART
    uart = UART(0, baudrate=115200, tx=Pin(0))
    
    print("\n[Core 0] Ready. Send data via USB serial...")
    print("Note: Message limited to ~10 chars due to small key size")
    print("-" * 50)
    
    while True:
        try:
            data = input("Enter text to encrypt: ")
            if not data:
                continue
            
            data_bytes = data.encode('utf-8')
            total_len = len(data_bytes)
            
            print(f"\n[INPUT] '{data}' ({total_len} bytes)")
            
            # RSA encrypt
            start_time = time.ticks_ms()
            encrypted_blocks = rsa_encrypt_bytes(data_bytes, RSA_PUBLIC_KEY)
            total_time = time.ticks_diff(time.ticks_ms(), start_time)
            
            print(f"\n[RSA] Encrypted {len(encrypted_blocks)} blocks in {total_time}ms")
            
            # Show encrypted blocks
            for i, block in enumerate(encrypted_blocks):
                print(f"  Block {i}: {block}")
            
            # Prepare transmission: [num_blocks][block1][block2]...
            num_blocks = len(encrypted_blocks)
            transmission = bytearray()
            transmission.extend(num_blocks.to_bytes(1, 'big'))
            
            for block in encrypted_blocks:
                # Send each block as 2 bytes (for our small key size)
                transmission.extend(block.to_bytes(2, 'big'))
            
            # Send over UART
            uart.write(transmission)
            
            print(f"[UART TX] Sent {len(transmission)} bytes to Pico 2")
            print("-" * 50)
            
        except Exception as e:
            print(f"[ERROR] {e}")
            import sys
            sys.print_exception(e)
            time.sleep_ms(100)

if __name__ == "__main__":
    main()
