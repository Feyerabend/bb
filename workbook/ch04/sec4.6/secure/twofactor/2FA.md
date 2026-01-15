
## 2FA Authentication System

This system provides secure two-factor authentication using Time-based One-Time
Passwords (TOTP) based on RFC 6238, with visual feedback through the
Pimoroni Display Pack 2.0.

```
               HTTPS
Python Client  ---->  Pico (2)W Server      Hardware Tokens
               <----                ^--------^
               JSON                  Same TOTP
```


### Authentication Flow


```mermaid
sequenceDiagram
    participant C as Client
    participant S as Server

    %% Step 1: Password Authentication
    C->>S: POST /api/auth/login<br>{username, password}
    activate S
    Note over S: Verify credentials<br>Check rate limits<br>Generate challenge token
    S-->>C: 200 OK<br>{status: "2fa_required",<br>challenge_token: "..."}
    deactivate S

    %% Step 2: TOTP Verification
    C->>S: POST /api/auth/verify<br>{challenge_token, totp_code: "123456"}
    activate S
    Note over S: Verify TOTP code<br>Check time drift (±30s)<br>Create session token
    S-->>C: 200 OK<br>{status: "success",<br>session_token: "...",<br>expires_in: 3600}
    deactivate S

    %% Step 3: Accessing Protected Resources
    C->>S: GET /api/dashboard<br>Authorization: Bearer {session_token}
    activate S
    Note over S: Validate session token<br>Check expiration
    S-->>C: 200 OK<br>{dashboard data}
    deactivate S
```

```mermaid
sequenceDiagram
    participant C as Client
    participant S as Server

    C->>+S: 1. POST /api/auth/login<br>{username, password}
    S->>S: Verify credentials + rate limit
    S->>S: Generate challenge token
    S-->>-C: 200 OK + challenge_token

    C->>+S: 2. POST /api/auth/verify<br>{challenge_token, totp_code}
    S->>S: Validate TOTP (±30s window)
    S->>S: Create session token
    S-->>-C: 200 OK + session_token (expires_in)

    C->>+S: 3. GET /api/...<br>Authorization: Bearer {token}
    S->>S: Validate & check expiration
    S-->>-C: 200 OK + protected data
```


### Testing the System

#### 1. Start the Server
```bash
## Flash server code to Pico W
## Server displays IP address and stats
```

#### 2. Generate TOTP Code
```bash
## On hardware token or run Python demo
python client.py
## Shows: "Demo TOTP: 123456"
```

#### 3. Authenticate
```bash
python client.py
## Enter credentials
## Enter TOTP code from hardware token
## Success: Access granted
```

#### 4. Test Rate Limiting
```bash
## Try wrong password 6 times
## Result: Account locked for 5 minutes
```



### Production Considerations & Project Suggestions

For real-world deployment, add:
1. *Use mbedtls* for proper crypto (HMAC-SHA1, AES, etc.)
2. *HTTPS certificates* - use Let's Encrypt or self-signed (often easier)
3. *Password hashing* - use bcrypt or Argon2
4. *Database storage* - use LittleFS or external database
5. *Logging* - store authentication attempts securely
6. *Backup codes* - for TOTP device loss
7. *Multi-factor recovery* - email/SMS backup
8. *Hardware security* - secure boot, encrypted storage


