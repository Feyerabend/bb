from machine import Pin, UART
import time
import _thread
from collections import deque

class UARTController:
    def __init__(self, uart_id=1, baudrate=9600, tx_pin=4, rx_pin=5):
        self.uart = UART(uart_id, baudrate=baudrate, tx=Pin(tx_pin), rx=Pin(rx_pin))
        
        # Buffers
        self.rx_buffer = deque((), 50)
        self.tx_buffer = deque((), 50)
        
        # Control flags
        self.running = True
        self.rx_lock = False
        self.tx_lock = False
        
        # Command history
        self.command_history = []
    
    def format_message(self, message):
        return f"#{message}*"
    
    def parse_message(self, raw_message):
        if raw_message.startswith('#') and raw_message.endswith('*'):
            return raw_message[1:-1]
        return None
    
    def rx_thread(self):
        print("Controller RX Thread started")
        buffer = ""
        
        while self.running:
            try:
                if self.uart.any():
                    data = self.uart.read()
                    if data:
                        buffer += data.decode('utf-8')
                        
                        # Process complete messages
                        while '#' in buffer and '*' in buffer:
                            start_idx = buffer.find('#')
                            end_idx = buffer.find('*', start_idx)
                            
                            if start_idx != -1 and end_idx != -1:
                                raw_message = buffer[start_idx:end_idx+1]
                                message = self.parse_message(raw_message)
                                
                                if message:
                                    while self.rx_lock:
                                        time.sleep(0.001)
                                    self.rx_lock = True
                                    
                                    if len(self.rx_buffer) >= 50:
                                        self.rx_buffer.popleft()
                                    self.rx_buffer.append((message, time.time()))
                                    
                                    self.rx_lock = False
                                
                                buffer = buffer[end_idx+1:]
                            else:
                                break
                
                time.sleep(0.01)
                
            except Exception as e:
                print(f"Controller RX error: {e}")
                time.sleep(0.1)
    
    def tx_thread(self):
        print("Controller TX Thread started")
        
        while self.running:
            try:
                message_to_send = None
                
                while self.tx_lock:
                    time.sleep(0.001)
                self.tx_lock = True
                
                if self.tx_buffer:
                    message_to_send = self.tx_buffer.popleft()
                
                self.tx_lock = False
                
                if message_to_send:
                    formatted = self.format_message(message_to_send)
                    self.uart.write(formatted.encode('utf-8'))
                    print(f"Sent: {message_to_send}")
                    
                    # Add to history
                    self.command_history.append((message_to_send, time.time()))
                    if len(self.command_history) > 20:
                        self.command_history.pop(0)
                
                time.sleep(0.01)
                
            except Exception as e:
                print(f"Controller TX error: {e}")
                time.sleep(0.1)
    
    def send_command(self, command):
        message = f"CMD:{command}"
        
        while self.tx_lock:
            time.sleep(0.001)
        self.tx_lock = True
        
        if len(self.tx_buffer) >= 50:
            self.tx_buffer.popleft()
        self.tx_buffer.append(message)
        
        self.tx_lock = False
    
    def send_request(self, request):
        message = f"REQ:{request}"
        
        while self.tx_lock:
            time.sleep(0.001)
        self.tx_lock = True
        
        if len(self.tx_buffer) >= 50:
            self.tx_buffer.popleft()
        self.tx_buffer.append(message)
        
        self.tx_lock = False
    
    def get_received_messages(self):
        messages = []
        
        while self.rx_lock:
            time.sleep(0.001)
        self.rx_lock = True
        
        while self.rx_buffer:
            messages.append(self.rx_buffer.popleft())
        
        self.rx_lock = False
        return messages
    
    def display_messages(self):
        messages = self.get_received_messages()
        for message, timestamp in messages:
            print(f"[{time.localtime(timestamp)[3]:02d}:{time.localtime(timestamp)[4]:02d}:{time.localtime(timestamp)[5]:02d}] Received: {message}")
    
    def interactive_mode(self):
        print("\n-- UART Controller --")
        print("Commands:")
        print("  STATUS    - Get device status")
        print("  PING      - Ping device")
        print("  LED_ON    - Turn LED on")
        print("  LED_OFF   - Turn LED off")
        print("  TEMP      - Request temperature")
        print("  HISTORY   - Show command history")
        print("  MESSAGES  - Show recent messages")
        print("  QUIT      - Exit")
        print("------------------------")
        
        while self.running:
            try:
                # Display any new messages
                self.display_messages()
                
                # Get user input
                cmd = input("Enter command: ").strip().upper()
                
                if cmd == "QUIT":
                    break
                elif cmd == "STATUS":
                    self.send_command("STATUS")
                elif cmd == "PING":
                    self.send_command("PING")
                elif cmd == "LED_ON":
                    self.send_command("LED_ON")
                elif cmd == "LED_OFF":
                    self.send_command("LED_OFF")
                elif cmd == "TEMP":
                    self.send_request("TEMP")
                elif cmd == "HISTORY":
                    print("\nCommand History:")
                    for i, (command, timestamp) in enumerate(self.command_history[-10:]):
                        print(f"  {i+1}. [{time.localtime(timestamp)[3]:02d}:{time.localtime(timestamp)[4]:02d}:{time.localtime(timestamp)[5]:02d}] {command}")
                elif cmd == "MESSAGES":
                    print("Recent messages displayed above")
                elif cmd == "":
                    continue
                else:
                    print(f"Unknown command: {cmd}")
                
                time.sleep(0.1)
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {e}")
    
    def start(self):
        print("UART Controller Starting..")
        print("TX=GP4, RX=GP5")
        
        # Start threads
        _thread.start_new_thread(self.rx_thread, ())
        _thread.start_new_thread(self.tx_thread, ())
        
        time.sleep(1)  # Let threads start
        
        try:
            self.interactive_mode()
        finally:
            self.stop()
    
    def monitor_mode(self):
        print("Monitor Mode - Press Ctrl+C to exit")
        
        try:
            while self.running:
                self.display_messages()
                time.sleep(0.5)
        except KeyboardInterrupt:
            pass
    
    def stop(self):
        print("\nStopping controller..")
        self.running = False

# Usage
if __name__ == "__main__":
    controller = UARTController()
    
    # Choose mode
    print("Select mode:")
    print("1. Interactive mode (send commands)")
    print("2. Monitor mode (just listen)")
    
    try:
        choice = input("Enter choice (1 or 2): ").strip()
        
        if choice == "1":
            controller.start()  # Interactive mode
        elif choice == "2":
            # Start threads for monitor mode
            _thread.start_new_thread(controller.rx_thread, ())
            _thread.start_new_thread(controller.tx_thread, ())
            controller.monitor_mode()
        else:
            print("Invalid choice")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        controller.stop()
