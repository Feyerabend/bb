
## Password Similarity Detection System

This system enforces *password diversity* during password changes by preventing
users from choosing new passwords that are too similar to their previous ones.
It uses the *Levenshtein distance algorithm* to measure textual similarity
between passwords and rejects changes that don't meet a minimum differentiation
threshold.

The obvious downside of this that plaintext of passwords needs to be compared.
See below.


### How It Works

__1. Similarity Measurement__

The system calculates a *similarity ratio* (0.0 to 1.0) between the old and new passwords:
- *1.0* = Identical passwords
- *0.7+* = Very similar (typically rejected)
- *0.5* = Moderately similar
- *0.0* = Completely different

__2. Levenshtein Distance__

Measures the minimum number of single-character edits (insertions, deletions, substitutions)
needed to transform one string into another.

*Example:*
- `Summer2024!` -> `Summer2025!`
- Only 1 character changed (4->5)
- Similarity: *91%* -> REJECTED

__3. Security Hashing__
Once a password passes similarity checks, it's hashed using *PBKDF2-HMAC-SHA256* with 10,000
iterations, making it (for today) computationally expensive to crack.



### Real-World Use Cases

__*Mandatory Password Resets*__

When organisations (incl. companies) require periodic password changes (e.g., every 90 days),
users often make minimal modifications like:
- `Password123` -> `Password124`
- `Winter2024!` -> `Spring2024!`
- `CompanyName1` -> `CompanyName2`

This system *prevents* these weak variations and forces meaningful changes.

__*Security Breach Response*__

After a credential leak or security incident:
- Require password resets across all accounts
- Block reuse of compromised passwords
- Prevent trivial variations that attackers could easily guess


__*User Guidance During Reset*__

The system can provide *real-time feedback*:

```
NO "MyPass2024" is too similar to your previous password (85% match)
NO "P@ssword123" is too similar (92% match)
YES "Tr0pic4lM00n$et" is sufficiently different
```

__*Compliance Requirements*__

Many security standards (NIST, PCI-DSS, HIPAA) recommend or require
preventing password history reuse. This extends that protection to *near-matches*.


### Implementation Strategies

__For Password Reset Systems__

```
1. User requests password reset
2. System retrieves hash of CURRENT password
3. User enters NEW password
4. System computes similarity(current, new)
5. If similarity > 70%:
   -> Reject with specific guidance
   -> Show examples of what makes passwords "different enough"
6. If acceptable:
   -> Hash and store new password
   -> Invalidate old sessions
```

__Privacy-Preserving Approach__

*Important:* The system needs access to the *plaintext*
old password for comparison, which creates challenges:

*Option A: During Password Change Flow*
- User must enter BOTH old and new passwords
- Compare before hashing
- *Never store plaintext*

*Option B: One-Way Hash Comparison (Limited)*
- Can only check exact matches (password history)
- Cannot detect similarity without plaintext access
- Less effective but more privacy-preserving


### Advantages & Limitations

Pros:
- *Prevents lazy password changes* that provide false security  
- *Educates users* about what makes passwords truly different  
- *Reduces attack surface* by eliminating predictable patterns  
- *Minimal computational overhead* (Levenshtein is fast)  
- *Language/character-agnostic* (works with any alphabet)

Cons:
- *Requires plaintext comparison* - Old password must be temporarily available  
- *May frustrate users* - Requires effort to create genuinely different passwords  
- *Doesn't prevent semantic similarity* - Can't detect `DogLover1` vs `CatLover1`  
- *Threshold tuning needed* - Too strict = user frustration; too loose = ineffective


### Recommended Thresholds

Based on security research:

- *< 60% similar*: Always accept
- *60-70% similar*: Warning, but allow
- *> 70% similar*: Reject and require different password
- *> 90% similar*: Strong rejection with educational message


__Pattern Detection__

Could be extended to detect common patterns:
- Sequential increments: `Pass2023` -> `Pass2024`
- Simple character substitution: `Password` -> `P@ssw0rd`
- Keyboard walks: `qwerty` -> `asdfgh`


__User Feedback Examples__

```
Your new password is too similar. Avoid:
- Changing only numbers (2024 -> 2025)
- Adding/removing a single character
- Simple character substitutions (a -> @)

Instead, try:
+ Using a completely different phrase
+ Combining 3-4 unrelated words
+ Using a password manager to generate random passwords
```


### Deployment Scenarios

__1. Corporate Environment__
- Reset passwords quarterly
- Block trivial changes
- Log similarity metrics for compliance auditing

__2. High-Security Systems__
- Banking, healthcare, government
- Stricter thresholds (reject > 60% similarity)
- Combine with MFA requirements

__3. Consumer Applications__
- Gentler thresholds (70-80%)
- Educational prompts rather than hard blocks
- Optional security score display


### Code Portability

The implementation shown is:
- *Embedded-friendly* (main.c): Runs on Raspberry Pi Pico (ARM Cortex-M0+)
- *Desktop-compatible* (desktop.c): Works on Mac/Linux/Windows with gcc
- *Dependency-free*: No external crypto libraries needed
- *Production-ready*: Real SHA-256 and PBKDF2 implementations


### Conclusion

Password similarity detection is a *practical, low-cost security enhancement*
that addresses a common vulnerability: users making trivial modifications during
mandatory password changes. While not a silver bullet, it significantly raises
the bar for attackers attempting to exploit password reuse patterns and helps
guide users toward genuinely stronger security practices.

*Best combined with:*
- Password strength requirements (length, complexity)
- Multi-factor authentication
- Password manager recommendations
- User security education
