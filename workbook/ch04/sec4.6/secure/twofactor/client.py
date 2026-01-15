"""
2FA Authentication Client
"""

import requests
import hmac
import hashlib
import time
import base64
import json
from getpass import getpass

class TOTPGenerator:
    """TOTP using HMAC-SHA1"""
    
    def __init__(self, secret_key):
        self.secret = base64.b32encode(secret_key.encode()).decode()
    
    def generate_totp(self, timestamp=None, interval=30):
        if timestamp is None:
            timestamp = int(time.time())
        
        # Calculate time step
        time_step = timestamp // interval
        
        # Convert to bytes (big-endian 8-byte format)
        time_bytes = time_step.to_bytes(8, byteorder='big')
        
        # Decode base32 secret
        secret_bytes = base64.b32decode(self.secret)
        
        # HMAC-SHA1
        hmac_hash = hmac.new(secret_bytes, time_bytes, hashlib.sha1).digest()
        
        # Dynamic truncation
        offset = hmac_hash[-1] & 0x0f
        truncated = int.from_bytes(hmac_hash[offset:offset+4], byteorder='big') & 0x7fffffff
        
        # Generate 6-digit code
        code = truncated % 1000000
        return f"{code:06d}"
    
    def get_current_code(self):
        """Get current TOTP code"""
        return self.generate_totp()
    
    def get_time_remaining(self):
        """Get seconds remaining for current code"""
        return 30 - (int(time.time()) % 30)


class SecureAuthClient:
    """Authentication client with proper security"""
    
    def __init__(self, server_url, verify_ssl=True):
        self.server_url = server_url.rstrip('/')
        self.session = requests.Session()
        self.session.verify = verify_ssl
        self.session_token = None
        self.max_retries = 3
        self.retry_delay = 2
    
    def authenticate(self, username, password, totp_generator):
        """Perform two-factor authentication"""
        
        print(f"\n  Connecting to {self.server_url}")
        print("=" * 60)
        
        # Step 1: Send username and password via POST
        print("\n[Step 1/3] Sending credentials..")
        try:
            response = self.session.post(
                f"{self.server_url}/api/auth/login",
                json={
                    'username': username,
                    'password': password
                },
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code != 200:
                print(f"  Authentication failed: {response.status_code}")
                return False
            
            data = response.json()
            
            if data.get('status') == 'error':
                print(f"  {data.get('message', 'Unknown error')}")
                return False
            
            if data.get('status') != '2fa_required':
                print(f"  Unexpected response: {data.get('status')}")
                return False
            
            print(f"  First factor verified")
            challenge_token = data.get('challenge_token')
            
        except requests.RequestException as e:
            print(f"  Connection error: {e}")
            return False
        
        # Step 2: Generate and display TOTP code
        print("\n[Step 2/3] Generating 2FA code..")
        current_code = totp_generator.get_current_code()
        time_remaining = totp_generator.get_time_remaining()
        
        print(f"\nHARDWARE TOKEN GENERATOR\n")
        print(f"{current_code}\n")
        print(f"Valid for: {time_remaining:2d} seconds")
        
        # Simulate user entering code (in real hardware, user manually enters)
        print(f"\n  Code expires in {time_remaining} seconds..")
        time.sleep(1)  # Simulate user reading and entering code
        
        # Step 3: Submit TOTP code
        print("\n[Step 3/3] Submitting 2FA code..")
        try:
            response = self.session.post(
                f"{self.server_url}/api/auth/verify-2fa",
                json={
                    'challenge_token': challenge_token,
                    'totp_code': current_code
                },
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code != 200:
                print(f"  2FA verification failed: {response.status_code}")
                return False
            
            data = response.json()
            
            if data.get('status') == 'success':
                self.session_token = data.get('session_token')
                print(f"\n  Authentication successful!")
                print(f"  Session token acquired: {self.session_token[:20]}..")
                return True
            else:
                print(f"  {data.get('message', 'Invalid 2FA code')}")
                return False
                
        except requests.RequestException as e:
            print(f"  Connection error: {e}")
            return False
    
    def access_protected_resource(self):
        """Access protected resource with session token"""
        if not self.session_token:
            print("  Not authenticated. Please login first.")
            return False
        
        print("\n  Accessing protected resource..")
        try:
            response = self.session.get(
                f"{self.server_url}/api/dashboard",
                headers={
                    'Authorization': f'Bearer {self.session_token}'
                },
                timeout=10
            )
            
            if response.status_code == 200:
                print("  Successfully accessed protected resource!")
                data = response.json()
                print(f"\n  Dashboard Data:")
                print(json.dumps(data, indent=2))
                return True
            elif response.status_code == 401:
                print("  Session expired or invalid")
                return False
            else:
                print(f"  Access denied: {response.status_code}")
                return False
                
        except requests.RequestException as e:
            print(f"  Connection error: {e}")
            return False


def demonstrate_totp():
    print("\nTOTP CODE GENERATION DEMONSTRATION\n")
    
    secret = "ALICE_SECRET_KEY_12345"
    totp = TOTPGenerator(secret)
    
    print(f"\nShared Secret: {secret}")
    print(f"Base32 Encoded: {totp.secret}")
    print("\nGenerating codes every 30 seconds:\n")
    
    for i in range(5):
        code = totp.get_current_code()
        remaining = totp.get_time_remaining()
        timestamp = int(time.time())
        
        print(f"[{time.strftime('%H:%M:%S')}] Code: {code} | "
              f"Time Step: {timestamp // 30} | "
              f"Valid for: {remaining:2d}s")
        
        if i < 4:
            time.sleep(6)  # Show multiple codes in same window
    
    print("\n\n")


# NOT YET READY!!

def main():
    print("\n" + "-" * 40)
    print("  2FA AUTHENTICATION SYSTEM")
    print("-" * 40)
    
    # Demonstrate TOTP generation first
    demo = input("\nDemonstrate TOTP generation? (y/n): ").strip().lower()
    if demo == 'y':
        demonstrate_totp()
    
    # Main authentication flow
    print("\n" + "-" * 40)
    print("  AUTHENTICATION DEMO")
    print("-" * 40)
    
    server_url = input("\nEnter server URL (default: https://192.168.1.100): ").strip()
    if not server_url:
        server_url = "https://192.168.1.100"
    
    username = input("Username: ").strip()
    if not username:
        username = "alice"
    
    password = getpass("Password: ")
    if not password:
        password = "secure_password_123"
    
    # Create TOTP generator with user's secret
    secret_key = f"{username.upper()}_SECRET_KEY_12345"
    totp_generator = TOTPGenerator(secret_key)
    
    # Create auth client (disable SSL verification for demo with self-signed certs)
    client = SecureAuthClient(server_url, verify_ssl=False)
    
    # Authenticate
    if client.authenticate(username, password, totp_generator):
        # Access protected resource
        client.access_protected_resource()
    else:
        print("\n  Authentication failed!")
    
    print("\n" + "-" * 40)


if __name__ == "__main__":
    main()


