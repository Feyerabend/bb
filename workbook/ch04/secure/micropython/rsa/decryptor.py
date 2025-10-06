# RSA DECRYPTOR
# Asymmetric decryption using RSA private key
# Wiring: UART RX (GP1) -> Pico1 TX, GND -> GND

import _thread
import time
from machine import UART, Pin

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

# RSA private key (matches the public key from encryptor)
RSA_PRIVATE_KEY = {
    'n': 3233,      # p * q (53 * 61)
    'd': 2753       # Private exponent (calculated from e, p, q)
}

# To verify the math:
# p = 53, q = 61
# n = p * q = 3233
# phi = (p-1) * (q-1) = 52 * 60 = 3120
# e = 17 (public exponent)
# d = 2753 (private exponent, where e*d ≡ 1 mod phi)

# Shared data structures
decrypt_queue = []
result_queue = []
core1_ready = False
lock = _thread.allocate_lock()

# Core 1: RSA decryption worker
def core1_task():
    global core1_ready
    print("[Core 1] RSA crypto engine started")
    core1_ready = True
    
    while True:
        if decrypt_queue:
            with lock:
                data = decrypt_queue.pop(0)
            
            cipher_int, n, d = data
            
            # Perform RSA decryption: m = c^d mod n
            start = time.ticks_ms()
            decrypted = pow_mod(cipher_int, d, n)
            duration = time.ticks_diff(time.ticks_ms(), start)
            
            with lock:
                result_queue.append((decrypted, duration))
            
            print(f"[Core 1] Decrypted block in {duration}ms")
        
        time.sleep_ms(5)

# RSA decrypt blocks (Core 0)
def rsa_decrypt_blocks(encrypted_blocks, private_key):
    n = private_key['n']
    d = private_key['d']
    
    # Calculate block size
    max_block_size = (n.bit_length() - 1) // 8
    
    decrypted_data = bytearray()
    
    for i, cipher_int in enumerate(encrypted_blocks):
        # Send to Core 1 for decryption
        with lock:
            decrypt_queue.append((cipher_int, n, d))
        
        # Wait for result
        while True:
            with lock:
                if result_queue:
                    msg_int, duration = result_queue.pop(0)
                    break
            time.sleep_ms(5)
        
        # Convert integer back to bytes
        # Calculate actual byte length needed
        byte_length = (msg_int.bit_length() + 7) // 8
        if byte_length == 0:
            byte_length = 1
        
        block_bytes = msg_int.to_bytes(byte_length, 'big')
        decrypted_data.extend(block_bytes)
    
    return bytes(decrypted_data)


def main():
    global core1_ready
    
    print("=" * 50)
    print("PICO 2 RSA DECRYPTOR - Asymmetric Crypto")
    print("=" * 50)
    print(f"RSA Private Key (n={RSA_PRIVATE_KEY['n']}, d={RSA_PRIVATE_KEY['d']})")
    print(f"Key size: {RSA_PRIVATE_KEY['n'].bit_length()} bits")
    print("\nWiring:")
    print("  GP1 (UART RX) -> Pico1 TX")
    print("  GND -> GND")
    print("=" * 50)
    
    # Start Core 1 crypto engine
    _thread.start_new_thread(core1_task, ())
    
    while not core1_ready:
        time.sleep_ms(100)
    
    # Setup UART
    uart = UART(0, baudrate=115200, rx=Pin(1))
    
    print("\n[Core 0] Ready. Listening for encrypted data...")
    print("-" * 50)
    
    buffer = bytearray()
    expected_blocks = None
    blocks_received = []
    
    while True:
        if uart.any():
            chunk = uart.read()
            buffer.extend(chunk)
            
            # Parse messages
            while len(buffer) > 0:
                # Read number of blocks if we don't have it
                if expected_blocks is None:
                    if len(buffer) < 1:
                        break
                    expected_blocks = buffer[0]
                    buffer = buffer[1:]
                    blocks_received = []
                    print(f"[UART RX] Expecting {expected_blocks} encrypted blocks")
                
                # Read blocks (2 bytes each for our small key size)
                bytes_per_block = 2
                
                if len(buffer) >= bytes_per_block:
                    block_bytes = buffer[:bytes_per_block]
                    buffer = buffer[bytes_per_block:]
                    
                    block_int = int.from_bytes(block_bytes, 'big')
                    blocks_received.append(block_int)
                    
                    print(f"  Block {len(blocks_received)}: {block_int}")
                    
                    # Check if we have all blocks
                    if len(blocks_received) == expected_blocks:
                        print(f"\n[RSA] Received all {expected_blocks} blocks")
                        
                        # Decrypt all blocks
                        start_time = time.ticks_ms()
                        decrypted_data = rsa_decrypt_blocks(blocks_received, RSA_PRIVATE_KEY)
                        total_time = time.ticks_diff(time.ticks_ms(), start_time)
                        
                        print(f"[RSA] Decrypted in {total_time}ms")
                        
                        # Display result
                        try:
                            plaintext = decrypted_data.decode('utf-8')
                            print(f"\n[DECRYPTED] '{plaintext}'")
                            print("[STATUS] ✓ Decryption successful!")
                        except:
                            print(f"[DECRYPTED] {decrypted_data.hex()}")
                            print("[STATUS] ✗ Not valid UTF-8")
                        
                        print("-" * 50)
                        
                        # Reset for next message
                        expected_blocks = None
                        blocks_received = []
                else:
                    # Wait for more data
                    break
        
        time.sleep_ms(10)

if __name__ == "__main__":
    main()
