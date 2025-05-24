
## Error Correction

In early computing systems, every byte of memory was often stored with an extra bit: *the parity bit*.
This bit ensured the total number of ones in the byte was either even (*even parity*) or odd
(*odd parity*). During read/write operations, hardware would verify parity. A mismatch triggered
an error signal, halting execution. But parity could only *detect* single-bit errors, not correct them.
Despite this limitation, parity checking became standard in 1960s-70s mainframe and minicomputer
memory systems, and even optional in some 1980s home computers.

*Error correction* emerged as a discipline to ensure data integrity amid noise, corruption, or
interference during transmission/storage. Early engineers faced unreliable communication channels--crackling
telephone lines, staticky radio transmissions--and needed methods to recover flipped bits in messages.

As data moved beyond local machines via telephone lines and networks, simple parity proved insufficient.
*Checksums* offered a scalable solution: a mathematical summary (e.g., summing bytes modulo 256) appended
to messages. Protocols like XMODEM and TCP/IP adopted checksums to verify packet integrity. However,
checksums had weaknesses--small changes could cancel out undetected--leading to the rise of
*CRC (Cyclic Redundancy Check)*. CRC treated data as a binary polynomial, dividing it by a generator
polynomial to produce a robust fingerprint. It became ubiquitous in Ethernet, disk storage, and
embedded systems for detecting burst errors and subtle bit flips.


#### Hamming Codes: The First Correction

Frustrated by error-induced delays on early computers, Richard Hamming devised the *Hamming code* in the
1950s. By strategically placing parity bits at power-of-two positions, overlapping data groups could
pinpoint and correct single-bit errors. For example, the *Hamming (7,4) code* encodes 4 data bits
into 7 bits, enabling single-error correction:

```python
def hamming_encode(data_bits):
    assert len(data_bits) == 4, "Only 4 data bits allowed"
    d = list(map(int, data_bits))
    
    # Calc parity bits using XOR
    p1 = d[0] ^ d[1] ^ d[3]   # Covers positions 1,3,5,7 (1-indexed)
    p2 = d[0] ^ d[2] ^ d[3]   # Covers positions 2,3,6,7
    p3 = d[1] ^ d[2] ^ d[3]   # Covers positions 4,5,6,7
    
    # Arrange bits: [p1, p2, d1, p3, d2, d3, d4]
    return [p1, p2, d[0], p3, d[1], d[2], d[3]]
```

```python
def hamming_decode(codeword):
    assert len(codeword) == 7, "Invalid codeword length"
    c = list(map(int, codeword))
    
    # Calc syndrome bits by checking parity groups
    s1 = c[0] ^ c[2] ^ c[4] ^ c[6]  # p1's group
    s2 = c[1] ^ c[2] ^ c[5] ^ c[6]  # p2's group
    s3 = c[3] ^ c[4] ^ c[5] ^ c[6]  # p3's group
    
    # Convert syndrome to decimal position (1-indexed)
    syndrome = (s3 << 2) | (s2 << 1) | s1
    
    if syndrome != 0:
        # Correct the error (convert to 0-indexed)
        c[syndrome-1] ^= 1
    
    # Extract original data bits from positions 3,5,6,7 (0-indexed: 2,4,5,6)
    return [c[2], c[4], c[5], c[6]]
```

This innovation laid the groundwork for *ECC (Error-Correcting Code) memory*, used in DEC VAXes and IBM
servers to correct single-bit errors and detect double-bit errors using parity-derived "syndrome"
calculations.


#### Handling Complex Errors

As systems faced *burst errors* (multiple consecutive bit corruptions), stronger methods emerged:
*Reed-Solomon Coding*.

Treating data blocks as polynomials over finite fields (Galois fields), Reed-Solomon could recover
entire corrupted chunks. It became vital for CDs (scratches), deep-space communication, and QR codes:

```python
from reedsolo import RSCodec

rsc = RSCodec(10)  # can correct up to 5 byte errors in a message

message = b"HelloWorld"
encoded = rsc.encode(message)
print("Encoded:", encoded)

# Introduce errors
corrupted = bytearray(encoded)
corrupted[0] ^= 0xFF
corrupted[5] ^= 0xAA
corrupted[12] ^= 0x42

print("Corrupted:", corrupted)

# Decode and correct
decoded = rsc.decode(corrupted)
print("Decoded:", decoded)
```

This Reed-Solomon example shows how symbol-level error correction can recover a message
even with multiple corrupted bytes. It uses polynomial algebra under finite fields
(Galois fields), which is why it's more powerful but also more complex.

```python
# Constants
FIELD_SIZE = 256
PRIMITIVE_POLY = 0x11d  # x^8 + x^4 + x^3 + x^2 + 1

# Galois Field tables
exp = [0] * (FIELD_SIZE * 2)
log = [0] * FIELD_SIZE

def init_tables():
    x = 1
    for i in range(FIELD_SIZE - 1):
        exp[i] = x
        log[x] = i
        x <<= 1
        if x & 0x100:
            x ^= PRIMITIVE_POLY
    for i in range(FIELD_SIZE - 1, FIELD_SIZE * 2):
        exp[i] = exp[i - (FIELD_SIZE - 1)]

init_tables()

def gf_add(x, y): return x ^ y
def gf_sub(x, y): return x ^ y
def gf_mul(x, y): return 0 if x == 0 or y == 0 else exp[log[x] + log[y]]
def gf_div(x, y): return 0 if x == 0 else exp[(log[x] - log[y]) % 255]
def gf_pow(x, power): return exp[(log[x] * power) % 255]
def gf_inv(x): return exp[255 - log[x]]

def poly_scale(p, x):
    return [gf_mul(c, x) for c in p]

def poly_add(p, q):
    r = [0] * max(len(p), len(q))
    for i in range(len(p)):
        r[i + len(r) - len(p)] = p[i]
    for i in range(len(q)):
        r[i + len(r) - len(q)] ^= q[i]
    return r

def poly_mul(p, q):
    r = [0] * (len(p) + len(q) - 1)
    for j in range(len(q)):
        for i in range(len(p)):
            r[i + j] ^= gf_mul(p[i], q[j])
    return r

def rs_generator_poly(nsym):
    g = [1]
    for i in range(nsym):
        g = poly_mul(g, [1, exp[i]])
    return g

def rs_encode_msg(msg, nsym):
    gen = rs_generator_poly(nsym)
    msg_out = msg + [0] * nsym
    for i in range(len(msg)):
        coef = msg_out[i]
        if coef != 0:
            for j in range(len(gen)):
                msg_out[i + j] ^= gf_mul(gen[j], coef)
    return msg + msg_out[-nsym:]

# Evaluate polynomial at x using Horner's method
def poly_eval(poly, x):
    y = poly[0]
    for i in range(1, len(poly)):
        y = gf_mul(y, x) ^ poly[i]
    return y

# Berlekamp-Massey and Chien search not shown for brevity

# Demo
init_tables()
message = [ord(c) for c in "HelloWorld"]
encoded = rs_encode_msg(message, nsym=10)

print("Encoded:", encoded)

# Introduce 3 byte errors
corrupted = encoded[:]
corrupted[0] ^= 0xFF
corrupted[5] ^= 0xAA
corrupted[12] ^= 0x42

print("Corrupted:", corrupted)

# Note: decoder not included, only just encoder and corruptor
```

#### Convolutional Codes & Viterbi Decoding  

Used in real-time systems like early space probes and GSM networks, convolutional codes combined
current and past input bits. The *Viterbi algorithm* then reconstructed the most likely original
message from noisy signals.

Let's take a minimal example: decoding a sequence of observations from a system that can
be in two hidden states: Rainy and Sunny. Observations are walk, shop, or clean.

```python
states = ['Rainy', 'Sunny']
observations = ['walk', 'shop', 'clean']
start_probability = {'Rainy': 0.6, 'Sunny': 0.4}

transition_probability = {
   'Rainy' : {'Rainy': 0.7, 'Sunny': 0.3},
   'Sunny' : {'Rainy': 0.4, 'Sunny': 0.6},
}

emission_probability = {
   'Rainy' : {'walk': 0.1, 'shop': 0.4, 'clean': 0.5},
   'Sunny' : {'walk': 0.6, 'shop': 0.3, 'clean': 0.1},
}
```

Here's the Viterbi decoder:

```python
def viterbi(obs, states, start_p, trans_p, emit_p):
    V = [{}]
    path = {}

    # Init base cases (t == 0)
    for s in states:
        V[0][s] = start_p[s] * emit_p[s][obs[0]]
        path[s] = [s]

    # Run Viterbi for t > 0
    for t in range(1, len(obs)):
        V.append({})
        new_path = {}

        for curr_state in states:
            (prob, state) = max(
                (V[t-1][prev_state] * trans_p[prev_state][curr_state] * emit_p[curr_state][obs[t]], prev_state)
                for prev_state in states
            )
            V[t][curr_state] = prob
            new_path[curr_state] = path[state] + [curr_state]

        path = new_path

    # Find the most probable path
    n = len(obs) - 1
    (prob, state) = max((V[n][s], s) for s in states)
    return prob, path[state]
```

Usage:

```python
obs_sequence = ['walk', 'shop', 'clean']
prob, state_path = viterbi(obs_sequence, states, start_probability, transition_probability, emission_probability)

print(f"Most likely hidden states: {state_path}")
print(f"Probability of path: {prob:.5f}")
```

This implementation tracks probabilities in a time-indexed dictionary (V), builds paths
dynamically, and chooses the most probable one at the end. The power of the Viterbi
algorithm lies in how it prunes the exponential search space down to a linear one using
optimal substructure.


#### Modern Advances

By the 1990s, error correction approached Claude Shannon's theoretical limits. *Turbo codes* and
*LDPC (Low-Density Parity Check)* codes used probabilistic techniques and iterative decoding to
minimise overhead while maximising reliability. LDPC now underpins Wi-Fi 6 and 5G networks.


Storage & Systemic Resilience:
- *ZFS Filesystem*: Combines SHA-256 checksums with RAID-Z redundancy to detect/correct "bit rot" on disks.  
- *Erasure Coding*: Splits data across distributed nodes (e.g., Amazon S3) to survive hardware failures,
  using Reed-Solomon or LRC (Local Reconstruction Codes).  
- *Hardware Integration*: Modern SSDs employ BCH/LDPC codes; server RAM uses ECC; CPUs include CRC32
  instructions.

### Summary

- *Hamming*: Simple, bitwise correction for RAM/embedded systems.  
- *Reed-Solomon*: Heavyweight symbol-level correction for bursts (CDs, space).  
- *LDPC/Viterbi*: Near-optimal efficiency for modern wireless.  

From parity bits to planetary-scale erasure coding, error correction ensures data survives
interference--even when the universe itself seems adversarial.




```python
# Simple Reed-Solomon implementation (non-optimised, for small cases)
# This implementation is for GF(2^8) with primitive polynomial 0x11d

# Galois Field GF(256) setup
PRIMITIVE_POLY = 0x11d
GF_SIZE = 256

# Precompute logs and anti-logs
exp = [0] * (2 * GF_SIZE)
log = [0] * GF_SIZE

x = 1
for i in range(GF_SIZE - 1):
    exp[i] = x
    log[x] = i
    x <<= 1
    if x & 0x100:
        x ^= PRIMITIVE_POLY

for i in range(GF_SIZE - 1, 2 * GF_SIZE):
    exp[i] = exp[i - GF_SIZE + 1]

def gf_add(x, y):
    return x ^ y

def gf_sub(x, y):
    return x ^ y

def gf_mul(x, y):
    if x == 0 or y == 0:
        return 0
    return exp[log[x] + log[y]]

def gf_div(x, y):
    if y == 0:
        raise ZeroDivisionError()
    if x == 0:
        return 0
    return exp[(log[x] - log[y]) % 255]

def gf_pow(x, power):
    return exp[(log[x] * power) % 255]

def gf_inv(x):
    return exp[255 - log[x]]

def poly_scale(p, x):
    return [gf_mul(c, x) for c in p]

def poly_add(p, q):
    r = [0] * max(len(p), len(q))
    for i in range(len(p)):
        r[i + len(r) - len(p)] = p[i]
    for i in range(len(q)):
        r[i + len(r) - len(q)] ^= q[i]
    return r

def poly_mul(p, q):
    r = [0] * (len(p) + len(q) - 1)
    for j in range(len(q)):
        for i in range(len(p)):
            r[i + j] ^= gf_mul(p[i], q[j])
    return r

def poly_eval(poly, x):
    y = poly[0]
    for i in range(1, len(poly)):
        y = gf_mul(y, x) ^ poly[i]
    return y

def rs_generator_poly(nsym):
    g = [1]
    for i in range(nsym):
        g = poly_mul(g, [1, exp[i]])
    return g

def rs_encode_msg(msg, nsym):
    gen = rs_generator_poly(nsym)
    msg_out = msg + [0] * nsym
    for i in range(len(msg)):
        coef = msg_out[i]
        if coef != 0:
            for j in range(len(gen)):
                msg_out[i + j] ^= gf_mul(gen[j], coef)
    return msg + msg_out[-nsym:]

def rs_calc_syndromes(msg, nsym):
    return [poly_eval(msg, exp[i]) for i in range(nsym)]

def rs_check(msg, nsym):
    return max(rs_calc_syndromes(msg, nsym)) == 0

# For now, decoder only detects if errors exist
# Correcting errors needs Berlekamp-Massey and Chien search

# Example
msg = [ord(c) for c in "HelloWorld"]
nsym = 10
enc = rs_encode_msg(msg, nsym)
print("Encoded:", enc)

# Introduce errors
corrupted = enc[:]
corrupted[0] ^= 0xFF
corrupted[5] ^= 0xAA
corrupted[12] ^= 0x42

print("Corrupted:", corrupted)
print("Syndromes:", rs_calc_syndromes(corrupted, nsym))
print("Check OK?", rs_check(corrupted, nsym))
```


..
