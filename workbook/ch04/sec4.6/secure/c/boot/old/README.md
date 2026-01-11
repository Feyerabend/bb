
## Secure Boot Chain Demonstration


| Concept | What it protects against | How it's shown in the demo | Real-world name / technique |
|---|---|---|---|
| Root of Trust (RoT) | Everything – the foundation | Simulated immutable ROM public key | Hardware RoT, eFuse/OTP burned keys |
| Chain of Trust | Malicious replacement of any stage | Each stage verifies the next one | Secure boot chain / authenticated boot |
| Digital Signature | Code tampering & impersonation | Very simplified Ed25519-like signature check | ECDSA, Ed25519, RSA-PSS |
| Image / Firmware Hash | Silent data corruption & substitution | SHA-like hash (very simplified) | SHA-256 + HMAC or plain SHA |
| Version Monotonic Counter | Rollback / downgrade attacks | Version stored in RAM (simulated flash/eFuse) | Anti-rollback, monotonic counters, RPMC |
| Public Key Infrastructure | Unauthorized code signing | Different keys for bootloader vs application | PKI, code signing certificates, key hierarchy |
| Defense in Depth | Single failure doesn't compromise whole system | Multiple independent checks (hash + sig + version) | Standard secure boot best practice |

A simple interactive demonstration running
*directly on Raspberry Pi Pico 2* + *Pimoroni Display Pack 2.0*
that walks you through five scenarios:

1. *Successful secure boot* – everything verifies, green success screen
2. *Tampered binary* – single byte flipped -> hash mismatch detected
3. *Rollback attack* – attacker tries to downgrade to vulnerable v1.0 after v2.0 was installed -> blocked
4. *Wrong / malicious signature* – attacker signs with his own key -> signature verification fails
5. *Chain of Trust overview* – animated diagram explaining who trusts/verifies whom

Controls (Pimoroni Display Pack 2.0 buttons):
- *A* -> next scenario
- *B* -> previous scenario
- *X* -> run selected scenario
- *Y* -> toggle auto-advance


### This is an educational demonstration

The code you see here is deliberately kept simple because its main purpose
is teaching, not providing actual security for a real product.

Many critical security features that would exist in a serious embedded
secure boot implementation are either completely absent or only symbolically present:

The cryptography used is extremely simplified--essentially just a toy XOR-based
transformation that serves as a stand-in for a real digital signature scheme.
In reality you would be using something like Ed25519, ECDSA or at minimum
properly padded RSA.

There is no real flash protection whatsoever. All "images" and metadata live in
regular RAM and disappear completely when power is removed. A real system would
need to protect code regions with hardware-enforced read-execute-only permissions
and usually write-protection fuses.

The version/anti-rollback counter is just a variable in RAM. In any serious
implementation this would live in non-volatile storage that is either one-time
programmable (eFuses/OTP), or uses wear-leveled flash with cryptographic integrity
and anti-rollback properties.

There is no concept of secure boot mode locking, no immutable first-stage bootloader
in hardware ROM, no hardware crypto acceleration, and--most importantly--no actual
jump to verified code. The demo only simulates the verification steps and shows
the pretty pictures on screen.

Finally, none of the constant-time properties, side-channel resistance, fault-injection
countermeasures or supply-chain hardening measures that are considered mandatory in
modern secure boot implementations are present here.

In short: everything that makes secure boot actually difficult and expensive to attack
is missing--by design. This is a classroom model, not a vault.


### How real projects grew out of similar educational demonstrations

Many production-grade secure boot systems that we use today started from prototypes
and educational projects that--at their beginning--looked conceptually very similar
to this demo.

Between roughly 2020–2025 several notable efforts followed more or less this path:


- *Tock OS* secure boot infrastructure moved from basic proof-of-concept verification
  code to full Ed25519 signatures with real monotonic counters stored in flash.

- *Google's Titan M* security chip (and later Titan chips) grew out of early prototyping
  work that initially used far simpler verification chains before moving to hardware-backed keys,
  fused root-of-trust and strong anti-rollback mechanisms.

- Espressif's *ESP32 Secure Boot v2* (and later variants) evolved from much simpler
  RSA-2048 based schemes into the current RSA-3072 + SHA-256 chain-of-trust model
  with proper eFuse anti-rollback protection.

- Nordic's *nRF Connect SDK* secure boot system standardized around MCUboot and added
  immutable bootloader regions plus persistent counters.

- The open-source *MCUboot* bootloader (heavily used by Zephyr RTOS and many other
  projects) started as a relatively simple, educational-style bootloader and gradually
  grew into one of the most widely deployed, production-oriented secure boot solutions
  for microcontrollers.

- Even some community projects like the *Pinecil* soldering iron firmware went through
  the classic journey: first toy signing demos -> community pressure -> proper image
  signing infrastructure with public verification keys.

In many cases the Raspberry Pi Pico / RP2040 community itself produced dozens of
similar educational secure-boot-with-display demos during 2022–2024, which served
as learning stepping stones for people who later worked on more serious security
architectures.


### Reality vs. this demonstration — a quick comparison

The difference between a toy demonstration like this one and a real-world
production secure boot system is substantial:

- Cryptography: simple reversible XOR scrambling vs battle-tested schemes
  (Ed25519, NIST P-256 ECDSA, RSA-PSS) combined with SHA-256 or SHA-512

- Anti-rollback/versioning: ordinary RAM variable that resets on power cycle
  vs eFuses, one-time-programmable bits, RPMC registers or cryptographically
  protected flash counters

- Signature verification code size: roughly 10–20 lines of toy code vs thousands
  of lines of carefully reviewed, constant-time, formally verified or side-channel
  hardened implementation

- Root key storage: ordinary C constant sitting in flash vs keys fused into silicon,
  stored in OTP memory, or provided by a hardware security module/secure element

- Firmware update mechanism: not implemented at all vs staged atomic updates, dual
  slots with fallback, anti-brick recovery paths, rollback protection

- What happens on failure: pretty red warning screen vs permanent boot lockout,
  factory recovery mode, or (in the worst case) bricking the device until physical
  recovery is performed


