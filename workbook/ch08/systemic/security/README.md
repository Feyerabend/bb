
## Security and Programming

Security in computing is often imagined in terms of firewalls, passwords, and encryption.
But beneath these mechanisms lies a deeper foundation: the *code* itself. Most digital
systems--whether web apps, operating systems, IoT devices, or embedded controllers--are
ultimately shaped by the programming languages, tools, and practices used to build them.
This makes programming not just a technical activity, but a frontline concern in cybersecurity.


To start-off, a small anecdote from years ago:

> I think it was around 1981. We were teenagers, maybe 16 or 17 years old, when we got the chance to do a school internship at a mainframe computer center. It felt like a dream come true--finally, a chance to spend time around a real mainframe. The hum of technology, the blinking lights, the rows of tape drives. We were thrilled.

> Of course, we were just kids, so we were only allowed to do basic tasks. Things the operators normally handled: mounting and removing magnetic tapes, installing those heavy disk packs, or sending short operator messages to users waiting for their batch jobs--things like: `*** SETUP ERROR ***` (in Swedish of course some mixture of languages: `*** FEL I SETUPEN ***`).  

> It was noisy--fans running constantly to cool down the machines--and the regular staff seemed to live off coffee: six, seven, even eight cups before lunch.

> But one thing stood out the most. *Security*. Or rather--the lack of it.

> The IBM 3033 mainframe, which processed massive national datasets, was housed in a lower-level server room. To get there, you simply took the elevator. And what was the access code to that floor? Yes. You guessed it: `3033`.

> Now, sure, most of the staff probably recognised each other. But people came and went. The high turnover, the constant background noise, the stress--it wouldn’t have been hard for an outsider to slip in unnoticed.

> And here’s the kicker:  
> That computer held Sweden’s entire national vehicle registry.

> All of it.

> No guards, no ID checks, no logs — just a code and a lift and the sound of cooling fans drowning out any question of security.

> So security hasn't always been in the focus. At this time they were more concerned about uptime, as some operators had their own pagers. Constantly accessible.


__Why Software Security Matters__

When systems fail, they often do so because of flaws in code:
- a misplaced pointer,
- an unchecked input,
- a flawed assumption about user behavior or concurrency.

In modern computing, most security vulnerabilities originate from software bugs, not hardware
failures or cryptographic breakthroughs. These bugs, in turn, are shaped by language design,
programmer skill, and development methodology.


__Security in Programming: Not an Add-on, but a Foundation__

Programming and security are intrinsically linked. Every programming decision--from memory
allocation to data validation--carries implicit security consequences. Unlike physical security
systems where defense can be layered externally, software security must often be built in,
not bolted on.

Historically, the industry treated security as a reactive process: patch after breach. But as
systems have become more complex and interconnected, that model has failed. Today's approach
emphasises proactive security through language design, automated analysis, and secure coding
principles.


### Programming Languages as Security Enablers or Risks

Some languages, like C and C++, give developers enormous power and low-level control—but at
the cost of manual memory management, unchecked buffer sizes, and undefined behavior. These
become fertile ground for vulnerabilities like:
- buffer overflows,
- use-after-free,
- integer underflows/overflows,
- race conditions.

Languages like Rust, Go, Ada/SPARK, and high-level managed environments like Java or TypeScript
try to constrain these risks through stronger type systems, memory safety guarantees, garbage
collection, or even formal verification.

In this way, a language becomes not just a tool for expressing logic—but a security framework,
shaping what kinds of bugs are easy, hard, or impossible to write.


__From Bugs to Breaches__

Many of the most devastating security incidents in computing history--Morris Worm, Heartbleed,
Log4j, SolarWinds--trace directly back to coding errors or oversights:
- Misused APIs
- Forgotten input validation
- Unsafe default settings
- Failure to check edge cases

These aren't abstract bugs. They become entry points for attackers, who exploit them to steal
data, hijack systems, or install malware.


### Security as a Systems and Human Issue

Finally, security isn't just about code or compilers. It's also about the practices, assumptions,
and incentives of the people building systems. Tools like static analyzers and memory-safe languages
are only effective if integrated into workflows, code reviews, and cultural expectations.

From Shift Left philosophies in DevSecOps to threat modeling and security education, secure
programming demands attention to people, processes, and principles, not just programming constructs.

[^shift]: "Shift Left" in DevSecOps means integrating security practices early in the software development
lifecycle--starting at the design, coding, and build stages rather than waiting until deployment or post-release.
This approach helps catch vulnerabilities sooner, reduces the cost of fixing them, and encourages developers
to take ownership of security alongside functionality.

The sections that follow summarise and touches on these issues across several layers:
- Core technical challenges in programming that lead to security issues
- Historical evolution of vulnerabilities and responses
- How language design contributes to—or protects against—vulnerabilities
- Preventive methods, tools, and best practices
- System-level defenses, including OS and compiler support
- Human and organizational dynamics that influence security outcomes
- And finally, emerging trends in hardware, language theory, and formal methods

Together, these show how the interplay of programming and security defines not just today's software,
but the trust we place in it.

The deeper analysis of the summary below, you can find in the document [Secure Programming](./Secure_Programming.docx).


### The Interplay of Security and Programming

Software security is inherently tied to programming practices, with vulnerabilities often arising from:  
- *Memory Management*: Manual handling in languages like C/C++ leads to buffer overflows,
  use-after-free errors, and data races.  
- *Input Handling*: Untrusted input enables SQL injection, XSS, and command injection.  
- *Concurrency*: Race conditions and resource exhaustion in multi-threaded systems.  
- *API Misuse*: Weak authentication, misconfigurations, or logical flaws expose systems to abuse.  

Approximately *70% of vulnerabilities stem from memory safety issues*, emphasising the need for safer languages and tools.


#### Historical Evolution of Vulnerabilities & Defenses

1. *1970s–1990s*: Early systems (UNIX, MS-DOS) lacked protections, leading to exploits like
   the *Morris Worm* (1988), which exploited buffer overflows.  
2. *2000s*: Network exposure expanded attack surfaces (e.g., *Code Red worm* targeting IIS).
   Microsoft's Secure Development Lifecycle (SDL) emerged.  
3. *2010s*: High-impact flaws like *Heartbleed* (OpenSSL) and *Spectre/Meltdown* (CPU side-channels)
   drove adoption of static analysis and sandboxing.  
4. *2020s+*: Shift toward *memory-safe languages* (Rust, Go) and formal verification. High-profile
   breaches (SolarWinds, Log4j) highlight supply-chain risks.  


#### Language-Level Security

- *Memory Safety*:  
  - *C/C++*: Manual management risks buffer overflows, null pointers.  
  - *Rust*: Ownership/borrowing system prevents data races and leaks at compile time.  
  - *Go*: Garbage collection and bounds-checked slices mitigate runtime errors.  
  - *Ada/SPARK*: Formal proofs ensure absence of runtime errors for critical systems.  
- *Type Safety*: Languages like Haskell and TypeScript enforce data integrity, reducing runtime surprises.  
- *Static Analysis*: Tools (e.g., Rust's borrow checker, Java annotations) catch vulnerabilities early.  

*Table 2* contrasts memory safety approaches across languages, highlighting trade-offs between performance and safety.


#### Preventive Methods

1. *Input Validation/Sanitization*: Whitelisting, parameterized queries, and encoding prevent injection attacks.  
2. *Memory Safety Tools*: AddressSanitizer, Valgrind, and fuzzers (AFL) detect runtime issues.  
3. *Static/Dynamic Analysis*: SAST (code scanning) and DAST (runtime testing) complement each other.  
4. *Least Privilege*: Restrict permissions for users, processes, and APIs.  
5. *Reproducible Builds & Immutable Infrastructure*: Ensure integrity and reduce supply-chain risks.  


#### System-Level Defenses

- *Compiler Protections*: ASLR, stack canaries, and DEP/NX hinder exploitation.  
- *Runtime Isolation*: Sandboxing (WebAssembly), Linux namespaces, and CHERI's hardware-enforced capabilities.  
- *Formal Verification*: Mathematically proven correctness (e.g., seL4 kernel, Amazon's s2n TLS).  

*Table 3* details compiler/runtime protections and their limitations (e.g., ASLR bypass via info leaks).


#### Human & Organisational Factors

- *Code Review/Threat Modeling*: STRIDE (threat identification) and DREAD (risk prioritization) frameworks.  
- *Secure Defaults*: HTTPS enforcement, least-privilege APIs.  
- *Shift-Left Security*: Integrate security early in development via DevSecOps, automated testing, and training.  

*Table 4* compares STRIDE (proactive threat categorization) and DREAD (quantitative risk scoring).


#### Future Trends

1. *Memory-Safe Languages*: Rust adoption in critical systems (Windows, Linux) reduces vulnerabilities.  
2. *Hardware-Assisted Security*: CHERI architecture enforces memory safety at the hardware level.  
3. *Formal Methods*: AI-driven tools may lower the cost of formal verification.  
4. *Security by Design*: Proactive practices replace reactive fixes, emphasizing resilience from inception.  


#### Conclusion

Secure programming demands a *multi-layered approach*:  
- *Technical*: Memory-safe languages, static analysis, and system-level protections.  
- *Process*: Threat modeling, reproducible builds, and immutable infrastructure.  
- *Human*: Training, code reviews, and a security-first culture.  

No single solution suffices; security is an ongoing process requiring adaptation to evolving threats.
The shift from reactive to proactive strategies--embracing memory safety, formal methods, and hardware
innovations--will define the next era of secure software.


- THe Chaos Report

