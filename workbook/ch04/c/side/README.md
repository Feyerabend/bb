
## Side-Channel Attacks

Side-channel attacks (SCAs) are a class of security exploits that target
the physical implementation of cryptographic systems rather than their
mathematical foundations. Unlike traditional attacks that rely on brute
force or algorithmic weaknesses, SCAs extract sensitive information 
(like encryption keys or passwords) by analyzing "side channels"--unintended
data leaks from hardware operations.

- *Timing Information*: Variations in execution time based on secret data,
  such as early exits in comparisons or cache hits/misses.
- *Power Consumption*: Differences in energy usage during computations,
  often correlated with the Hamming weight (number of 1s) in binary data.
- *Electromagnetic Emissions*: Radiation patterns that reveal internal states.
- *Sound or Heat*: Acoustic or thermal signatures from processing.

These attacks are particularly insidious because they can bypass strong
encryption *without* directly cracking it. Famous examples include the timing
attack on RSA in OpenSSL (1995) and power analysis attacks like Differential
Power Analysis (DPA) on smart cards. Mitigations often involve constant-time
algorithms, masking, or hardware shielding to make operations independent
of secret data.


### Projects

This repository contains a hands-on demonstration of side-channel attacks and
countermeasures, implemented on the Raspberry Pi Pico 2 microcontroller with
the Pimoroni Display Pack 2.0. The demo visualises vulnerabilities in cryptographic
operations through interactive modes, using the display for graphs, status updates
and explanations, while simulating power traces with external LEDs.

Features:
- *Timing Attack on Password Comparison*: Shows how a vulnerable early-exit
  string comparison leaks correct prefix length via timing differences.
  Contrasts with a secure constant-time implementation.
- *Timing Attack on AES S-Box*: Demonstrates cache-timing vulnerabilities in
  AES lookups, with variable delays simulating hits/misses.
- *Power Analysis Simulation*: Uses Hamming weight to mimic power consumption
  during XOR operations, visualised on bars and LEDs to show how it leaks
  secret key bits.
- *Countermeasures Overview*: Displays techniques like constant-time code,
  masking, blinding, noise injection, and hardware defenses.


Here are a few beginner-friendly project ideas to build on this code:

1. *Add Electromagnetic Attack Simulation*: Integrate a simple RF sensor
   or use the Pico's ADC to measure simulated EM leaks (e.g., from a coil
   near the board). Update the display to graph EM traces alongside power.
   
2. *Real AES Implementation with SCA Tools*: Expand the AES demo to a full
   encryption routine using the Pico's hardware accelerator (if available)
   or a library like TinyAES. Add support for capturing real timing data
   via USB serial and analyze it with tools like ChipWhisperer-Lite.

3. *Gamified SCA Challenge*: Turn it into an interactive game where users
   "attack" the system by guessing keys based on displayed timings/power.
   Add scoring, hints, and more complex secrets to teach SCA principles.

4. *IoT Security Auditor*: Modify for wireless demos--use the Pico's UART
   to simulate a secure communication protocol, then demonstrate side-channel
   leaks over a network. Integrate with e.g. ESP32 for Wi-Fi logging of attack data.
