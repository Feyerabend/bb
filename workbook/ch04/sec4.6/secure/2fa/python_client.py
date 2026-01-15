
# python_client.py test

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
        """
        Step 1: Login with username and password
        Returns session info if password is correct
        """
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
                print(f"✓ Password accepted!")
                print(f"  Session ID: {self.session_id}")
                print(f"  {data['message']}")
                return data
            else:
                print(f"✗ Login failed: {data['message']}")
                return data
                
        except Exception as e:
            print(f"✗ Connection error: {e}")
            return {"status": "error", "message": str(e)}
    
    def verify_token(self, token: str) -> dict:
        """
        Step 2: Verify 2FA token from Device A
        """
        if not self.session_id:
            print("✗ No active session. Login first.")
            return {"status": "error", "message": "No session"}
        
        print(f"\n[Step 2] Verifying token {token}...")
        
        try:
            response = requests.post(
                f"{self.server_url}/verify",
                json={"session_id": self.session_id, "token": token},
                timeout=10  # Longer timeout as it validates with Device A
            )
            
            data = response.json()
            
            if data["status"] == "success":
                print(f"✓ Authentication successful!")
                print(f"  Welcome, {data['username']}!")
                return data
            else:
                print(f"✗ Verification failed: {data['message']}")
                return data
                
        except Exception as e:
            print(f"✗ Connection error: {e}")
            return {"status": "error", "message": str(e)}
    
    def check_status(self) -> dict:
        """
        Check authentication status of current session
        """
        if not self.session_id:
            print("✗ No active session")
            return {"status": "error", "message": "No session"}
        
        try:
            response = requests.post(
                f"{self.server_url}/status",
                json={"session_id": self.session_id},
                timeout=5
            )
            
            data = response.json()
            
            if data["status"] == "ok":
                auth_status = "Authenticated ✓" if data["authenticated"] else "Pending 2FA"
                print(f"\nSession Status:")
                print(f"  User: {data['username']}")
                print(f"  Status: {auth_status}")
            
            return data
            
        except Exception as e:
            print(f"✗ Connection error: {e}")
            return {"status": "error", "message": str(e)}


def print_banner():
    """Print client banner"""
    print("=" * 60)
    print("  2FA Authentication Client (Device C)")
    print("=" * 60)


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
                print("\n👉 Now go to Device A, enter PIN, and get the token!")
            
        elif choice == "2":
            if not client.session_id:
                print("✗ Please login first (option 1)")
                continue
                
            token = input("Enter 6-digit token from Device A: ").strip()
            
            if len(token) != 6 or not token.isdigit():
                print("✗ Token must be 6 digits")
                continue
            
            result = client.verify_token(token)
            
            if result["status"] == "success":
                print("\n🎉 You are now fully authenticated!")
                print("    In a real system, you'd now have access to protected resources.")
            
        elif choice == "3":
            client.check_status()
            
        elif choice == "4":
            print("\nGoodbye!")
            break
            
        else:
            print("Invalid choice")


def demo_mode(server_ip: str):
    """Automated demo showing the full flow"""
    print_banner()
    print("\n🎬 Running automated demo...")
    
    client = AuthClient(server_ip)
    
    # Step 1: Login
    print("\n" + "=" * 60)
    result = client.login("alice", "password123")
    
    if result["status"] != "pending":
        print("Demo failed at login step")
        return
    
    time.sleep(2)
    
    # Step 2: Wait for user to get token
    print("\n" + "=" * 60)
    print("\n⏸️  PAUSED - Manual step required:")
    print("    1. Go to Device A (Token Service)")
    print("    2. Enter PIN using buttons: A=1, B=2, X=3, Y=4")
    print("    3. Default PIN is '1234' (buttons: A, B, X, Y)")
    print("    4. Read the 6-digit token from the display")
    print("    5. Enter it below")
    
    token = input("\nEnter token: ").strip()
    
    # Step 3: Verify token
    print("\n" + "=" * 60)
    result = client.verify_token(token)
    
    if result["status"] == "success":
        time.sleep(1)
        
        # Step 4: Check status
        print("\n" + "=" * 60)
        client.check_status()
        
        print("\n✅ Demo complete!")
        print("\nThis demonstrated:")
        print("  • Something you know (password)")
        print("  • Something you have (Device A with PIN)")
        print("  • Server validation (Device B)")


if __name__ == "__main__":
    import sys
    
    # Configuration
    SERVER_IP = "192.168.1.101"  # IP of Device B
    
    if len(sys.argv) > 1:
        SERVER_IP = sys.argv[1]
    
    print(f"Server IP: {SERVER_IP}")
    print("\nMode:")
    print("  1. Interactive mode")
    print("  2. Demo mode")
    
    mode = input("\nSelect mode (1/2): ").strip()
    
    if mode == "1":
        interactive_mode(SERVER_IP)
    elif mode == "2":
        demo_mode(SERVER_IP)
    else:
        print("Invalid mode")
