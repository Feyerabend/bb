import requests
import getpass
import time

def xor_encrypt(data, key):
    """Simple XOR encryption matching Pico implementation"""
    key_bytes = key.encode()
    data_bytes = data.encode()
    encrypted = bytearray()
    
    for i, byte in enumerate(data_bytes):
        encrypted.append(byte ^ key_bytes[i % len(key_bytes)])
    
    return encrypted.decode('latin1')

def authenticate_2fa(server_url, username, password):
    """Perform 2FA authentication"""
    
    # Encrypt credentials
    encrypted_user = xor_encrypt(username, "SHARED_KEY")
    encrypted_pass = xor_encrypt(password, "SHARED_KEY")
    
    print(f"Connecting to {server_url}")
    
    # Step 1: Send first factor (username/password)
    try:
        response = requests.get(f"{server_url}/login", params={
            'user': encrypted_user,
            'pass': encrypted_pass
        }, timeout=5)
        
        result = response.json()
        
        if result['status'] == 'error':
            print(f"Authentication failed: {result['message']}")
            return False
            
        elif result['status'] == '2fa_required':
            print(f"First factor verified: {result['message']}")
            
            # Step 2: Get 2FA code from user
            print("\nPlease generate 2FA code on your hardware token..")
            totp_code = input("Enter 6-digit 2FA code: ").strip()
            
            # Send second factor
            response = requests.get(f"{server_url}/login", params={
                'user': encrypted_user,
                'pass': encrypted_pass,
                'totp': totp_code
            }, timeout=5)
            
            result = response.json()
            
            if result['status'] == 'success':
                print(f"{result['message']}")
                return True
            else:
                print(f"2FA failed: {result['message']}")
                return False

    except requests.RequestException as e:
        print(f"Connection error: {e}")
        return False
    
    return False

def access_protected_resource(server_url):
    """Access the protected dashboard"""
    try:
        response = requests.get(f"{server_url}/dashboard", timeout=5)
        if response.status_code == 200:
            print("Successfully accessed protected resource!")
            print("Dashboard content received.")
        else:
            print("Access denied to protected resource")
    except requests.RequestException as e:
        print(f"Error accessing resource: {e}")

def main():
    server_ip = input("Enter Pico server IP address: ").strip()
    if not server_ip:
        server_ip = "192.168.1.100"  # Default
    
    server_url = f"http://{server_ip}"
    
    print("..> 2FA CLIENT LOGIN")
    print("..> Connecting to Pico Auth Server")
    
    username = input("\nUsername: ")
    password = getpass.getpass("Password: ")
    
    if authenticate_2fa(server_url, username, password):
        access_protected_resource(server_url)
    else:
        print("Authentication failed!")

if __name__ == "__main__":
    main()

