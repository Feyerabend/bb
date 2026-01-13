
## AES-CBC

*AES-CBC* (Advanced Encryption Standard in *Cipher Block Chaining* mode)
is one of the most classic and widely used ways to encrypt data longer
than a single block using AES.


### Quick Summary Table -- AES-CBC at a Glance

| Property                  | Description                                                                |
|---------------------------|----------------------------------------------------------------------------|
| Block size                | Always 128 bits (16 bytes) for AES                                         |
| Key sizes                 | 128, 192 or 256 bits                                                       |
| Needs IV?                 | Yes -- 128-bit (16 bytes), *must be unpredictable/random* for each message |
| Needs padding?            | Yes (when message length not multiple of 16 bytes)                         |
| Parallel encryption?      | *No* -- sequential (chaining dependency)                                   |
| Parallel decryption?      | *Yes*                                                                      |
| Hides patterns?           | Good (much better than ECB)                                                |
| Provides authentication?  | *No* -- only confidentiality                                               |
| Malleable?                | Yes -- bit-flipping attack possible                                        |
| Modern recommendation     | Mostly *legacy* -- prefer AES-GCM or ChaCha20-Poly1305 today               |


### How AES-CBC Works -- Step by Step

__Encryption__

```
P = plaintext (split into 16-byte blocks: P₁, P₂, ..., Pn)
C = ciphertext blocks
IV = Initialization Vector (16 random bytes -- never reuse with same key!)
Eₖ = AES encryption with key K

C₁ = Eₖ(P₁ ⊕ IV)
C₂ = Eₖ(P₂ ⊕ C₁)
C₃ = Eₖ(P₃ ⊕ C₂)
...
Cn = Eₖ(Pn ⊕ Cₙ₋₁)

Final output = IV || C₁ || C₂ || ... || Cn
```

*Important visual idea*:

```
IV ──⊕──► Eₖ ──► C₁
          ▲
P₁ ───────┘

          C₁ ──⊕──► Eₖ ──► C₂
                    ▲
          P₂ ───────┘

(and so on...)
```

The previous *ciphertext* is fed forward and *XOR*-ed
with the next plaintext block -> this is the "chaining".


__Decryption (very symmetric!)__

```
C₁ ──► Dₖ ──⊕──► P₁    (⊕ with IV)
C₂ ──► Dₖ ──⊕──► P₂    (⊕ with C₁)
C₃ ──► Dₖ ──⊕──► P₃    (⊕ with C₂)
...
```

Notice: decryption can be parallelized because you only
need the previous *ciphertext* block (which you already have).

```
IV ──⊕──► Dₖ( C₁ ) ──► P₁
C₁ ──⊕──► Dₖ( C₂ ) ──► P₂
C₂ ──⊕──► Dₖ( C₃ ) ──► P₃
...
```


### Why Do We Need Padding?

AES always works on *exactly 16 bytes*.

If your message is 50 bytes long -> you need 4 full blocks = 64 bytes.

-> You must *pad* the last 14 bytes.

*Most common padding today* (PKCS#7 / PKCS#5):

- Add N bytes, each with value N
- Examples:

```
"hello" (5 bytes) -> needs 11 bytes padding -> "hello" + 11 x 0x0B
123 bytes (7 full blocks + 11 bytes) -> pad with 5 bytes of 0x05
Exactly 128 bytes? -> add full block of 16 x 0x10 (very important!)
```

After decryption you look at the *last byte*, say it is 7 -> remove
last 7 bytes (and you should check they are all 0x07).


### Security Properties & Problems of AES-CBC

*Good properties*
- Hides repeating blocks much better than ECB
- Widely supported, battle-tested for 20+ years
- Decryption is parallelizable

*Serious weaknesses / gotchas (why it's considered legacy today)*

1. *No authentication / integrity*  
   Attacker can flip bits in ciphertext -> flips corresponding bits
   in plaintext after decryption (bit-flipping attack)

2. *Padding Oracle attacks* (very famous & practical!)  
   If server tells attacker (even indirectly) whether padding was
   correct -> can decrypt everything byte-by-byte
   -> Never decrypt unauthenticated CBC in protocols you control!

3. *Must use unpredictable IV* every time  
   Reusing IV + same key -> leaks whether first blocks are equal

4. *Cannot parallelize encryption*  
   Bad for very high-speed / multi-core scenarios


### Modern Recommendation (2025--2026 reality)

| Goal / Use-case                        | Recommended today                  | Why not CBC?                           |
|----------------------------------------|------------------------------------|----------------------------------------|
| Most new applications                  | *AES-GCM* or *ChaCha20-Poly1305*   | Built-in authentication + fast         |
| Legacy systems / compatibility         | AES-CBC + *HMAC* (Encrypt-then-MAC)| Very careful implementation required   |
| Very constrained devices (tiny memory) | ChaCha20-Poly1305                  | Smaller code size, no big tables       |
| Disk encryption                        | AES-XTS                            | Better for random access               |


### Quick Mnemonic

```
ECB -> Never use (patterns everywhere)
CBC -> "Classic But Careful" -- needs HMAC + random IV + proper padding handling
GCM -> "Great Choice Modern" -- confidentiality + authentication in one shot
```

Hope this gives you a clear mental picture of how AES-CBC really works — and why we mostly moved on to authenticated modes! 😄

Any particular part (padding, IV rules, attacks, comparison with GCM...) you want to go deeper into?