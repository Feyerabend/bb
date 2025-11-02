"""
Simple WiFi Access Point Test for Pico W
Run this on the SERVER Pico to verify WiFi works
"""
import network
import socket
import utime

def test_access_point():
    print("\n" + "="*40)
    print("WiFi AP TEST - SERVER")
    print("="*40)
    
    try:
        # Try setting country code
        try:
            import rp2
            print("Setting country code to US...")
            rp2.country('US')
            utime.sleep(0.5)
        except Exception as e:
            print(f"Country code warning: {e}")
        
        # Create Access Point
        print("\nCreating Access Point...")
        ap = network.WLAN(network.AP_IF)
        print(f"AP Object: {ap}")
        
        # Power cycle
        ap.active(False)
        utime.sleep(1)
        ap.active(True)
        print("AP activated")
        
        # Wait for AP to be active
        timeout = 10
        while not ap.active() and timeout > 0:
            print(f"Waiting for AP active... ({timeout}s)")
            utime.sleep(1)
            timeout -= 1
        
        if not ap.active():
            print("✗ FAILED: AP did not activate")
            print("Check: Do you have a Pico W (not regular Pico)?")
            print("Check: Is your firmware Pico W compatible?")
            return False
        
        print("✓ AP is active")
        
        # Configure AP
        ssid = "PicoTest"
        password = "test1234"
        
        print(f"\nConfiguring AP...")
        print(f"  SSID: {ssid}")
        print(f"  Password: {password}")
        
        ap.config(essid=ssid, password=password)
        utime.sleep(2)
        
        # Show configuration
        config = ap.ifconfig()
        print(f"\n✓ AP Configuration:")
        print(f"  IP Address: {config[0]}")
        print(f"  Netmask: {config[1]}")
        print(f"  Gateway: {config[2]}")
        print(f"  DNS: {config[3]}")
        
        print(f"\n✓ SUCCESS! AP is running")
        print(f"\nTry connecting from your phone/laptop:")
        print(f"  Network: {ssid}")
        print(f"  Password: {password}")
        
        # Simple TCP server test
        print(f"\nStarting test TCP server on port 8080...")
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(('0.0.0.0', 8080))
        server.listen(1)
        server.settimeout(30)  # 30 second timeout
        
        print(f"✓ Server listening")
        print(f"\nWaiting for connection (30s timeout)...")
        print(f"Try: telnet {config[0]} 8080")
        
        try:
            conn, addr = server.accept()
            print(f"\n✓ CLIENT CONNECTED: {addr}")
            conn.send(b"Hello from Pico!\r\n")
            conn.close()
            print("✓ Test message sent")
        except OSError as e:
            print(f"\nNo connection (timeout) - but server is working!")
            print(f"This is OK for testing")
        
        server.close()
        
        print("\n" + "="*40)
        print("TEST COMPLETE - AP WORKS!")
        print("="*40)
        return True
        
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import sys
        sys.print_exception(e)
        return False

# Run test
test_access_point()