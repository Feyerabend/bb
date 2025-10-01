# enhanced_sensor_node.py - environmental sensor node
import network, socket, time, json, _thread
from machine import Pin, I2C, unique_id
import gc
import ubinascii

# Sensor imports (adjust based on actual sensors)
# from bme280 import BME280  # temperature, humidity, pressure
# from ds18x20 import DS18X20  # temperature
# import onewire

REPORTING_INTERVAL = 10  # seconds between sensor readings
HEARTBEAT_INTERVAL = 30  # seconds between heartbeats
MAX_RETRY_ATTEMPTS = 3
RECONNECT_DELAY = 5

class SensorNode:
    def __init__(self):
        self.node_id = ubinascii.hexlify(unique_id()).decode()
        self.setup_network()
        self.setup_sensors()
        self.setup_communication()
        
        self.role = None
        self.coordinator_ip = "192.168.4.1"
        self.network_topology = {}
        self.last_heartbeat = 0
        self.last_data_send = 0
        self.sequence_num = 0
        self.connection_retries = 0
        
    def setup_network(self):
        """Connect to environmental network"""
        self.sta = network.WLAN(network.STA_IF)
        self.sta.active(True)
        
        while True:
            try:
                print("Connecting to EnviroNet..")
                self.sta.connect("EnviroNet", "sensor123")
                
                # Wait for connection with timeout
                timeout = 20
                while not self.sta.isconnected() and timeout > 0:
                    time.sleep(1)
                    timeout -= 1
                
                if self.sta.isconnected():
                    self.my_ip = self.sta.ifconfig()[0]
                    print(f"Connected! IP: {self.my_ip}")
                    self.connection_retries = 0
                    break
                else:
                    raise Exception("Connection timeout")
                    
            except Exception as e:
                self.connection_retries += 1
                print(f"Connection failed (attempt {self.connection_retries}): {e}")
                if self.connection_retries < MAX_RETRY_ATTEMPTS:
                    time.sleep(RECONNECT_DELAY)
                else:
                    print("Max connection attempts reached. Restarting..")
                    # In a real implementation, you might reset the device
                    time.sleep(30)
                    self.connection_retries = 0
    
    def setup_sensors(self):
        """Initialize sensor hardware"""
        self.sensors = {}
        
        try:
            # Example BME280 setup (adjust for actual sensors)
            # i2c = I2C(0, scl=Pin(1), sda=Pin(0))
            # self.bme = BME280(i2c=i2c)
            # self.sensors['bme280'] = ['temperature', 'humidity', 'pressure']
            
            # For demo purposes, we'll simulate sensors
            self.sensors = {
                'temperature': {'pin': None, 'type': 'analog'},
                'humidity': {'pin': None, 'type': 'i2c'},
                'pressure': {'pin': None, 'type': 'i2c'}
            }
            
            print(f"Initialized sensors: {list(self.sensors.keys())}")
            
        except Exception as e:
            print(f"Sensor initialization failed: {e}")
            self.sensors = {'temperature': {'pin': None, 'type': 'simulated'}}
    
    def setup_communication(self):
        """Setup communication sockets"""
        # Discovery socket
        self.discovery_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.discovery_sock.settimeout(2)
        
        # Data transmission socket
        self.data_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.data_sock.settimeout(2)
        
        # Peer communication socket
        self.peer_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.peer_sock.bind((self.my_ip, 5002))
        self.peer_sock.settimeout(0.1)
        
        # Start peer listener thread
        _thread.start_new_thread(self.listen_peers, ())
    
    def register_with_coordinator(self):
        """Register with the network coordinator"""
        try:
            message = {
                'type': 'REGISTER',
                'node_id': self.node_id,
                'node_info': {
                    'sensors': list(self.sensors.keys()),
                    'ip': self.my_ip,
                    'capabilities': ['environmental_monitoring']
                }
            }
            
            self.discovery_sock.sendto(json.dumps(message).encode(), 
                                     (self.coordinator_ip, 5000))
            
            # Wait for response
            data, addr = self.discovery_sock.recvfrom(1024)
            response = json.loads(data.decode())
            
            if response['type'] == 'TOPOLOGY':
                self.role = response['your_role']
                self.network_topology = response['nodes']
                print(f"Registered as {self.role}")
                print(f"Network topology: {self.network_topology}")
                return True
                
        except Exception as e:
            print(f"Registration failed: {e}")
            return False
    
    def read_sensors(self):
        """Read all available sensors"""
        readings = {}
        
        try:
            # Real sensor reading would go here
            # For BME280 example:
            # temp, pressure, humidity = self.bme.read_compensated_data()
            # readings = {
            #     'temperature': temp / 100.0,
            #     'pressure': pressure / 25600.0,
            #     'humidity': humidity / 1024.0
            # }
            
            # Simulated readings for demo
            import random
            base_temp = 20 + random.uniform(-5, 10)
            readings = {
                'temperature': round(base_temp + random.uniform(-2, 2), 1),
                'humidity': round(50 + random.uniform(-20, 30), 1),
                'pressure': round(1013 + random.uniform(-50, 50), 1)
            }
            
            # Add node-specific variation to make data more interesting
            node_offset = hash(self.node_id) % 10
            readings['temperature'] += node_offset * 0.5
            
        except Exception as e:
            print(f"Sensor reading failed: {e}")
            readings = {'error': str(e)}
            
        return readings
    
    def send_sensor_data(self, readings):
        """Send sensor data to coordinator"""
        try:
            message = {
                'type': 'SENSOR_DATA',
                'node_id': self.node_id,
                'sequence': self.sequence_num,
                'timestamp': time.time(),
                'data': readings
            }
            
            self.data_sock.sendto(json.dumps(message).encode(), 
                                (self.coordinator_ip, 5001))
            
            # Wait for acknowledgment
            try:
                data, addr = self.data_sock.recvfrom(1024)
                ack = json.loads(data.decode())
                if ack['type'] == 'DATA_ACK' and ack['sequence'] == self.sequence_num:
                    self.sequence_num += 1
                    return True
            except OSError:
                pass  # Timeout is OK, coordinator might be busy
                
        except Exception as e:
            print(f"Data transmission failed: {e}")
            
        return False
    
    def listen_peers(self):
        """Listen for messages from peer nodes"""
        while True:
            try:
                data, addr = self.peer_sock.recvfrom(1024)
                message = json.loads(data.decode())
                
                if message['type'] == 'PEER_SYNC':
                    # Handle synchronization messages
                    print(f"Sync from {addr[0]}: {message}")
                elif message['type'] == 'EMERGENCY_TAKEOVER':
                    # Handle coordinator failover
                    if self.role == 'MASTER':
                        print("Taking over coordination duties")
                        # Implement backup coordinator logic here
                        
            except (OSError, ValueError):
                pass
            
            time.sleep(0.1)
    
    def check_coordinator_health(self):
        """Ping coordinator to ensure it's alive"""
        try:
            ping_msg = {'type': 'HEARTBEAT', 'node_id': self.node_id}
            self.discovery_sock.sendto(json.dumps(ping_msg).encode(), 
                                     (self.coordinator_ip, 5000))
            return True
        except:
            return False
    
    def handle_coordinator_failure(self):
        """Handle coordinator failure - promote master node"""
        if self.role == 'MASTER':
            print("Coordinator failed, attempting to take over...")
            # Implement backup coordinator functionality
            # This could involve:
            # 1. Notifying all peer nodes
            # 2. Starting coordinator services
            # 3. Maintaining network state
        else:
            print("Coordinator failed, waiting for master node response...")
            # Wait for master to take over or timeout and elect new leader
    
    def run(self):
        """Main sensor node loop"""
        print(f"Starting sensor node {self.node_id}")
        
        # Initial registration
        while not self.register_with_coordinator():
            print("Registration failed, retrying...")
            time.sleep(5)
        
        coordinator_failures = 0
        
        while True:
            current_time = time.time()
            
            try:
                # Send sensor data periodically
                if current_time - self.last_data_send > REPORTING_INTERVAL:
                    readings = self.read_sensors()
                    
                    if self.send_sensor_data(readings):
                        print(f"Sent data: {readings}")
                        coordinator_failures = 0
                    else:
                        coordinator_failures += 1
                        print(f"Data send failed (failures: {coordinator_failures})")
                    
                    self.last_data_send = current_time
                
                # Send heartbeat
                if current_time - self.last_heartbeat > HEARTBEAT_INTERVAL:
                    if not self.check_coordinator_health():
                        coordinator_failures += 1
                    else:
                        coordinator_failures = 0
                    
                    self.last_heartbeat = current_time
                
                # Handle coordinator failure
                if coordinator_failures > 3:
                    print("Coordinator appears to be down")
                    self.handle_coordinator_failure()
                    coordinator_failures = 0  # Reset to avoid spam
                
                # Memory management
                if current_time % 60 < 1:  # Once per minute
                    gc.collect()
                
            except Exception as e:
                print(f"Main loop error: {e}")
            
            time.sleep(1)

# Start the sensor node
if __name__ == "__main__":
    node = SensorNode()
    node.run()
