"""
WiFi Diagnostic Script for Raspberry Pi Pico W
Run this on the CLIENT Pico to test if WiFi hardware is working
"""

import network
import utime
import gc

def test_wifi_hardware():
    print("\n" + "="*60)
    print(" "*15 + "WIFI HARDWARE DIAGNOSTIC")
    print("="*60)
    
    # System info
    try:
        import sys
        print(f"\nSystem Information:")
        print(f"  Platform: {sys.platform}")
        print(f"  Version: {sys.version}")
        print(f"  Implementation: {sys.implementation}")
        print(f"  Free memory: {gc.mem_free()} bytes")
    except:
        pass
    
    print("\n" + "-"*60)
    print("TEST 1: Check if network module exists")
    print("-"*60)
    try:
        print(f"✓ network module imported successfully")
        print(f"  Available: {dir(network)}")
    except Exception as e:
        print(f"✗ FAILED: {e}")
        return
    
    print("\n" + "-"*60)
    print("TEST 2: Disable all WiFi interfaces")
    print("-"*60)
    try:
        # Turn off AP
        ap = network.WLAN(network.AP_IF)
        if ap.active():
            print("  Disabling AP interface...")
            ap.active(False)
            utime.sleep(1)
        print("✓ AP interface disabled")
        
        # Turn off STA
        sta = network.WLAN(network.STA_IF)
        if sta.active():
            print("  Disabling STA interface...")
            sta.active(False)
            utime.sleep(1)
        print("✓ STA interface disabled")
        
    except Exception as e:
        print(f"✗ FAILED: {e}")
        import sys
        sys.print_exception(e)
        return
    
    print("\n" + "-"*60)
    print("TEST 3: Create STA interface")
    print("-"*60)
    try:
        wlan = network.WLAN(network.STA_IF)
        print("✓ STA interface created")
    except Exception as e:
        print(f"✗ FAILED: {e}")
        import sys
        sys.print_exception(e)
        return
    
    print("\n" + "-"*60)
    print("TEST 4: Activate STA interface")
    print("-"*60)
    try:
        wlan.active(True)
        print("  Waiting for activation...")
        
        max_wait = 10
        wait_count = 0
        while not wlan.active() and wait_count < max_wait:
            print(".", end="")
            utime.sleep(0.5)
            wait_count += 1
        
        if wlan.active():
            print(f"\n✓ STA interface activated (took {wait_count * 0.5:.1f}s)")
        else:
            print(f"\n✗ FAILED: Could not activate after {max_wait}s")
            return
            
    except Exception as e:
        print(f"✗ FAILED: {e}")
        import sys
        sys.print_exception(e)
        return
    
    print("\n" + "-"*60)
    print("TEST 5: Get interface information")
    print("-"*60)
    try:
        # MAC address
        try:
            mac = wlan.config('mac')
            mac_str = ':'.join(['%02X' % b for b in mac])
            print(f"✓ MAC Address: {mac_str}")
        except Exception as e:
            print(f"✗ Could not get MAC: {e}")
        
        # Status
        try:
            status = wlan.status()
            print(f"✓ Status: {status}")
        except Exception as e:
            print(f"✗ Could not get status: {e}")
        
        # Interface config
        try:
            config = wlan.ifconfig()
            print(f"✓ IP Config: {config[0]}")
        except Exception as e:
            print(f"✗ Could not get config: {e}")
            
    except Exception as e:
        print(f"✗ FAILED: {e}")
    
    print("\n" + "-"*60)
    print("TEST 6: WiFi Scan (CRITICAL TEST)")
    print("-"*60)
    print("This is the most important test!")
    print("Scanning for networks (may take 10-15 seconds)...")
    print("Please wait...\n")
    
    utime.sleep(3)  # Extra time for WiFi to stabilize
    
    try:
        networks = wlan.scan()
        
        if networks is None:
            print("✗ FAILED: Scan returned None")
            print("\n⚠ HARDWARE ISSUE DETECTED!")
            print("  The WiFi hardware may not be working.")
            print("  Possible causes:")
            print("  - WiFi chip not initialized (firmware issue)")
            print("  - Antenna problem")
            print("  - Hardware defect")
            return
        
        if len(networks) == 0:
            print("✗ FAILED: Scan returned 0 networks")
            print("\n⚠ HARDWARE OR ANTENNA ISSUE!")
            print("  The WiFi can scan but finds nothing.")
            print("  Possible causes:")
            print("  - Antenna disconnected/damaged")
            print("  - Shielded environment (metal case)")
            print("  - Too far from any WiFi networks")
            print("  - Wrong WiFi region/frequency")
            print("\nTry this:")
            print("  1. Bring a phone/laptop VERY close to the Pico")
            print("  2. Turn on a WiFi hotspot on your phone")
            print("  3. Run this test again")
            return
        
        print(f"✓ SUCCESS: Found {len(networks)} network(s)!\n")
        print("Networks detected:")
        print("-" * 60)
        
        for i, net in enumerate(networks):
            try:
                ssid = net[0].decode('utf-8') if isinstance(net[0], bytes) else net[0]
                bssid = ':'.join(['%02X' % b for b in net[1]]) if len(net) > 1 else '?'
                channel = net[2] if len(net) > 2 else '?'
                rssi = net[3] if len(net) > 3 else '?'
                security = net[4] if len(net) > 4 else '?'
                
                print(f"{i+1}. SSID: '{ssid}'")
                print(f"   RSSI: {rssi} dBm")
                print(f"   Channel: {channel}")
                print(f"   Security: {security}")
                print(f"   BSSID: {bssid}")
                print()
                
            except Exception as e:
                print(f"{i+1}. <parsing error: {e}>")
        
        print("=" * 60)
        print("✓ WiFi HARDWARE IS WORKING!")
        print("=" * 60)
        print("\nYour WiFi hardware is functioning correctly.")
        print("If you can't connect to the server AP:")
        print("  1. Make sure server is running FIRST")
        print("  2. Check that 'PicoImages' appears in the list above")
        print("  3. Try moving the Picos closer together")
        print("  4. Check server console for errors")
        
    except Exception as e:
        print(f"✗ FAILED: Scan crashed: {e}")
        import sys
        sys.print_exception(e)
        print("\n⚠ CRITICAL ERROR!")
        print("  The scan function crashed - this indicates:")
        print("  - Firmware bug")
        print("  - Hardware initialization failure")
        print("  - Memory corruption")
        return
    
    print("\n" + "-"*60)
    print("TEST 7: Cleanup")
    print("-"*60)
    try:
        wlan.active(False)
        print("✓ Interface deactivated")
    except:
        pass
    
    print("\n" + "="*60)
    print("DIAGNOSTIC COMPLETE")
    print("="*60)
    gc.collect()
    print(f"Final free memory: {gc.mem_free()} bytes")


if __name__ == "__main__":
    test_wifi_hardware()