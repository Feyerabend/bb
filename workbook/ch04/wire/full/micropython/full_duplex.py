from machine import Pin, UART, ADC
import time
import _thread
from collections import deque

class FullDuplexUART:
    def __init__(self, uart_id=1, baudrate=9600, tx_pin=4, rx_pin=5):
        self.uart = UART(uart_id, baudrate=baudrate, tx=Pin(tx_pin), rx=Pin(rx_pin))
        self.temp_sensor = ADC(4)
        self.led = Pin(25, Pin.OUT)
        
        # Buffers for incoming and outgoing messages
        self.rx_buffer = deque((), 50)  # max 50 messages
        self.tx_buffer = deque((), 50)
        
        # Control flags
        self.running = True
        self.counter = 0
        
        # Locks for thread safety (simple flags since MicroPython threading is limited)
        self.rx_lock = False
        self.tx_lock = False
    
    def read_temperature(self):
        reading = self.temp_sensor.read_u16()
        voltage = reading * 3.3 / 65535
        temperature = 27 - (voltage - 0.706) / 0.001721
        return round(temperature, 1)
    
    def blink_led(self, duration=0.1):
        self.led.on()
        time.sleep(duration)
        self.led.off()
    
    def format_message(self, message):
        return f"#{message}*"
    
    def parse_message(self, raw_message):
        if raw_message.startswith('#') and raw_message.endswith('*'):
            return raw_message[1:-1]
        return None
    
    def rx_thread(self):
        print("RX Thread started")
        buffer = ""
        
        while self.running:
            try:
                if self.uart.any():
                    data = self.uart.read()
                    if data:
                        buffer += data.decode('utf-8')
                        
                        # Look for complete messages
                        while '#' in buffer and '*' in buffer:
                            start_idx = buffer.find('#')
                            end_idx = buffer.find('*', start_idx)
                            
                            if start_idx != -1 and end_idx != -1:
                                raw_message = buffer[start_idx:end_idx+1]
                                message = self.parse_message(raw_message)
                                
                                if message:
                                    # Thread-safe buffer access
                                    while self.rx_lock:
                                        time.sleep(0.001)
                                    self.rx_lock = True
                                    
                                    if len(self.rx_buffer) >= 50:
                                        self.rx_buffer.popleft()  # remove oldest
                                    self.rx_buffer.append(message)
                                    
                                    self.rx_lock = False
                                
                                buffer = buffer[end_idx+1:]  # remove processed part
                            else:
                                break
                
                time.sleep(0.01)  # small delay to prevent busy waiting
                
            except Exception as e:
                print(f"RX Thread error: {e}")
                time.sleep(0.1)
    
    def tx_thread(self):
        print("TX Thread started")
        
        while self.running:
            try:
                # Check if there are messages to send
                message_to_send = None
                
                while self.tx_lock:
                    time.sleep(0.001)
                self.tx_lock = True
                
                if self.tx_buffer:
                    message_to_send = self.tx_buffer.popleft()
                
                self.tx_lock = False
                
                if message_to_send:
                    formatted_message = self.format_message(message_to_send)
                    self.uart.write(formatted_message.encode('utf-8'))
                    self.blink_led(0.05)  # quick blink for TX
                    print(f"Transmitted: {message_to_send}")
                
                time.sleep(0.01)  # small delay
                
            except Exception as e:
                print(f"TX Thread error: {e}")
                time.sleep(0.1)
    
    def send_message(self, message):
        while self.tx_lock:
            time.sleep(0.001)
        self.tx_lock = True
        
        if len(self.tx_buffer) >= 50:
            self.tx_buffer.popleft()  # remove oldest
        self.tx_buffer.append(message)
        
        self.tx_lock = False
    
    def get_received_message(self):
        while self.rx_lock:
            time.sleep(0.001)
        self.rx_lock = True
        
        message = None
        if self.rx_buffer:
            message = self.rx_buffer.popleft()
        
        self.rx_lock = False
        return message
    
    def process_received_messages(self):
        message = self.get_received_message()
        while message:
            print(f"Received: {message}")
            
            # Process different message types
            if message.startswith("CMD:"):
                self.handle_command(message[4:])
            elif message.startswith("REQ:"):
                self.handle_request(message[4:])
            
            message = self.get_received_message()
    
    def handle_command(self, command):
        print(f"Processing command: {command}")
        
        if command == "STATUS":
            temp_c = self.read_temperature()
            temp_f = (temp_c * 9/5) + 32
            status_msg = f"STATUS:TEMP={temp_c}C,COUNT={self.counter}"
            self.send_message(status_msg)
        elif command == "PING":
            self.send_message("PONG")
        elif command == "LED_ON":
            self.led.on()
            self.send_message("ACK:LED_ON")
        elif command == "LED_OFF":
            self.led.off()
            self.send_message("ACK:LED_OFF")
    
    def handle_request(self, request):
        print(f"Processing request: {request}")
        
        if request == "TEMP":
            temp_c = self.read_temperature()
            temp_f = (temp_c * 9/5) + 32
            self.send_message(f"TEMP:{temp_c}C,{temp_f:.1f}F")
    
    def start(self):
        print("Full-Duplex UART Communication Starting..")
        print("TX=GP4, RX=GP5")
        print("Commands: STATUS, PING, LED_ON, LED_OFF")
        print("Requests: TEMP")
        
        # Start RX and TX threads
        _thread.start_new_thread(self.rx_thread, ())
        _thread.start_new_thread(self.tx_thread, ())
        
        # Main loop - sends periodic temperature data and processes received messages
        try:
            while self.running:
                # Send periodic temperature data
                temp_c = self.read_temperature()
                temp_f = (temp_c * 9/5) + 32
                temp_message = f"TEMP:{temp_c}C,{temp_f:.1f}F,COUNT:{self.counter}"
                self.send_message(temp_message)
                
                # Process any received messages
                self.process_received_messages()
                
                self.counter += 1
                
                # Wait before next cycle
                for _ in range(20):  # 2 seconds total, checking for messages every 0.1s
                    self.process_received_messages()
                    time.sleep(0.1)
                
        except KeyboardInterrupt:
            print("\nStopping communication..")
            self.running = False
            time.sleep(0.5)  # Allow threads to finish
    
    def stop(self):
        self.running = False

# Usage
if __name__ == "__main__":
    comm = FullDuplexUART()
    comm.start()

