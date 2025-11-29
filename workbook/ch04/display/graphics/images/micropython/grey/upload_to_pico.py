import serial
import time
import sys

# Configuration - CHANGE THESE!
PORT = '/dev/ttyACM0'  # Linux/Mac, or 'COM3' on Windows
IMAGE_FILE = 'image.ppm'  # File on your computer
TARGET_PATH = '/image.ppm'  # Where to save on Pico

def send_file_to_pico(port, local_file, remote_path):
    """Upload a file to Pico using raw REPL"""
    
    # Read the file
    print(f"Reading {local_file}...")
    with open(local_file, 'rb') as f:
        data = f.read()
    
    print(f"File size: {len(data)} bytes")
    
    # Connect to Pico
    print(f"Connecting to {port}...")
    ser = serial.Serial(port, 115200, timeout=1)
    time.sleep(0.1)
    
    # Interrupt any running program
    ser.write(b'\r\x03\x03')  # Ctrl-C twice
    time.sleep(0.1)
    ser.read_all()
    
    # Enter raw REPL mode
    ser.write(b'\r\x01')  # Ctrl-A
    time.sleep(0.1)
    response = ser.read_all()
    
    if b'raw REPL' not in response:
        print("Failed to enter raw REPL mode")
        return False
    
    print("Uploading file...")
    
    # Send command to open file for writing
    cmd = f"f = open('{remote_path}', 'wb')\r\n"
    ser.write(cmd.encode())
    ser.write(b'\x04')  # Ctrl-D to execute
    time.sleep(0.1)
    ser.read_all()
    
    # Write data in chunks
    chunk_size = 256
    for i in range(0, len(data), chunk_size):
        chunk = data[i:i+chunk_size]
        cmd = f"f.write({repr(bytes(chunk))})\r\n"
        ser.write(cmd.encode())
        ser.write(b'\x04')
        time.sleep(0.05)
        ser.read_all()
        
        # Progress indicator
        progress = (i + chunk_size) * 100 // len(data)
        print(f"\rProgress: {min(progress, 100)}%", end='')
    
    print()
    
    # Close file
    ser.write(b"f.close()\r\n")
    ser.write(b'\x04')
    time.sleep(0.1)
    ser.read_all()
    
    # Exit raw REPL
    ser.write(b'\x02')  # Ctrl-B
    time.sleep(0.1)
    
    # Verify
    ser.write(b"import os\r\n")
    ser.write(f"print(os.stat('{remote_path}'))\r\n".encode())
    time.sleep(0.2)
    response = ser.read_all().decode('utf-8', errors='ignore')
    
    ser.close()
    
    print(f"\n✓ Upload complete!")
    print(f"Verification: {response}")
    return True

if __name__ == '__main__':
    try:
        send_file_to_pico(PORT, IMAGE_FILE, TARGET_PATH)
    except FileNotFoundError:
        print(f"Error: {IMAGE_FILE} not found!")
    except serial.SerialException as e:
        print(f"Error: Could not connect to {PORT}")
        print(f"Make sure the Pico is connected and the port is correct")
        print(f"Details: {e}")
    except Exception as e:
        print(f"Error: {e}")
