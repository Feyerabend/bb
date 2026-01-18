# python_client.py - Client for 2FA authentication system
# This runs on your PC/Mac and connects to Device B

import requests
import json
import time
from typing import Optional

class AuthClient:
    """Client for 2FA authentication system"""
    
    def __init__(self, server_ip: str, server_port: int = 9090):
        self.server_url = f"http://{server_ip}:{server_port}"
        self.session_id: Optional[str] = None
        self.username: Optional[str] = None
        
    def login(self, username: str, password: str) -> dict:
        """Step 1: Login with username and password"""
        print(f"\n[Step 1] Logging in as {username}...")
        
        try:
            response = requests.post(
                f"{self.server_url}/login",
                json={"username": username, "password": password},
                timeout=5
            )
            
            data = response.json()
            
            if data["status"] == "pending":
                self.session_id = data["session_id"]
                self.username = username
                print(f"    Password accepted!")
                print(f"  Session ID: {self.session_id}")
                print(f"  {data['message']}")
                return data
            else:
                print(f"    Login failed: {data['message']}")
                return data
                
        except Exception as e:
            print(f"    Connection error: {e}")
            return {"status": "error", "message": str(e)}
    
    def verify_token(self, token: str) -> dict:
        """Step 2: Verify 2FA token from Device A"""
        if not self.session_id:
            print("  No active session. Login first.")
            return {"status": "error", "message": "No session"}
        
        print(f"\n[Step 2] Verifying token {token}...")
        
        try:
            response = requests.post(
                f"{self.server_url}/verify",
                json={"session_id": self.session_id, "token": token},
                timeout=10
            )
            
            data = response.json()
            
            if data["status"] == "success":
                print(f"    Authentication successful!")
                print(f"  Welcome, {data['username']}!")
                return data
            else:
                print(f"    Verification failed: {data['message']}")
                return data
                
        except Exception as e:
            print(f"    Connection error: {e}")
            return {"status": "error", "message": str(e)}
    
    def check_status(self) -> dict:
        """Check authentication status"""
        if not self.session_id:
            print("  No active session")
            return {"status": "error", "message": "No session"}
        
        try:
            response = requests.post(
                f"{self.server_url}/status",
                json={"session_id": self.session_id},
                timeout=5
            )
            
            data = response.json()
            
            if data["status"] == "ok":
                auth_status = "  Authenticated" if data["authenticated"] else "⧗ Pending 2FA"
                print(f"\nSession Status:")
                print(f"  User: {data['username']}")
                print(f"  Status: {auth_status}")
            
            return data
            
        except Exception as e:
            print(f"    Connection error: {e}")
            return {"status": "error", "message": str(e)}


def print_banner():
    """Print client banner"""
    print("-" * 60)
    print("  2FA Authentication Client")
    print("-" * 60)


def interactive_mode(server_ip: str):
    """Interactive client mode"""
    print_banner()
    
    client = AuthClient(server_ip)
    
    print(f"\nConnecting to server at {server_ip}:9090")
    print("\nAvailable test users:")
    print("  - alice / password123")
    print("  - bob / secret456")
    
    while True:
        print("\n" + "-" * 60)
        print("Commands:")
        print("  1. Login (username + password)")
        print("  2. Verify token (from Device A)")
        print("  3. Check status")
        print("  4. Exit")
        print("-" * 60)
        
        choice = input("\nChoice: ").strip()
        
        if choice == "1":
            username = input("Username: ").strip()
            password = input("Password: ").strip()
            result = client.login(username, password)
            
            if result["status"] == "pending":
                print("\n  -> Now go to Device A, enter PIN, and get the token!")
            
        elif choice == "2":
            if not client.session_id:
                print("  Please login first (option 1)")
                continue
                
            token = input("Enter 6-digit token from Device A: ").strip()
            
            if len(token) != 6 or not token.isdigit():
                print("  Token must be 6 digits")
                continue
            
            result = client.verify_token(token)
            
            if result["status"] == "success":
                print("\n    You are now fully authenticated!")
            
        elif choice == "3":
            client.check_status()
            
        elif choice == "4":
            print("\nGoodbye!")
            break
            
        else:
            print("Invalid choice")


def demo_mode(server_ip: str):
    """Automated demo"""
    print_banner()
    print("\n Running automated demo...")
    
    client = AuthClient(server_ip)
    
    # Step 1: Login
    print("\n" + "-" * 60)
    result = client.login("alice", "password123")
    
    if result["status"] != "pending":
        print("Demo failed at login step")
        return
    
    time.sleep(2)
    
    # Step 2: Get token from user
    print("\n" + "-" * 60)
    print("\n    PAUSED - Manual step required:")
    print("    1. Go to Device A (Token Service)")
    print("    2. Enter PIN: 1234 (buttons A, B, X, Y)")
    print("    3. Read the 6-digit token from display")
    print("    4. Enter it below")
    
    token = input("\nEnter token: ").strip()
    
    # Step 3: Verify
    print("\n" + "-" * 60)
    result = client.verify_token(token)
    
    if result["status"] == "success":
        time.sleep(1)
        
        print("\n" + "-" * 60)
        client.check_status()
        
        print("\n Demo complete!")
        print("\nThis demonstrated two-factor authentication:")
        print("  - Something you know: password")
        print("  - Something you have: Device A with PIN")


if __name__ == "__main__":
    import sys
    
    print("\n" + "-" * 60)
    print("SETUP INSTRUCTIONS")
    print("-" * 60)
    print("\n1. Device A (Token Service):")
    print("   - Upload and run: token_service.py")
    print("   - Creates WiFi AP: '2FA_Token_Service'")
    print("   - Password: 'SecureToken2024'")
    print("   - IP will be: 192.168.4.1")
    print("\n2. Device B (Auth Server):")
    print("   - Upload and run: auth_server.py")
    print("   - Connects to Device A's WiFi")
    print("   - Check its display for IP address")
    print("\n3. This Client:")
    print("   - Needs Device B's IP address")
    print("-" * 60)
    
    if len(sys.argv) > 1:
        server_ip = sys.argv[1]
    else:
        server_ip = input("\nEnter Device B's IP address: ").strip()
        if not server_ip:
            print("Error: IP address required")
            sys.exit(1)
    
    print(f"\nConnecting to: {server_ip}")
    print("\nSelect mode:")
    print("  1. Interactive mode")
    print("  2. Demo mode")
    
    mode = input("\nChoice (1/2): ").strip()
    
    if mode == "1":
        interactive_mode(server_ip)
    elif mode == "2":
        demo_mode(server_ip)
    else:
        print("Invalid mode")


