# enhanced_ap.py - Robust environmental monitoring coordinator
import network, socket, time, json
from machine import Pin, I2C
import gc

# Config
NODE_TIMEOUT = 30  # seconds before considering node dead
DATA_RETENTION = 100  # max sensor readings to keep
ALERT_THRESHOLDS = {
    'temperature': {'min': 10, 'max': 35},
    'humidity': {'min': 30, 'max': 80},
    'pressure': {'min': 950, 'max': 1050}
}

class EnvironmentalCoordinator:
    def __init__(self):
        self.setup_ap()
        self.setup_sockets()
        self.nodes = {}  # ip -> {role, last_seen, sensors, data_history}
        self.alerts = []
        self.sequence_num = 0
        
    def setup_ap(self):
        self.ap = network.WLAN(network.AP_IF)
        self.ap.config(essid="EnviroNet", password="sensor123")
        self.ap.active(True)
        self.ap_ip = self.ap.ifconfig()[0]
        print(f"Environmental Network AP: {self.ap_ip}")
        
    def setup_sockets(self):
        # Discovery socket
        self.discovery_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.discovery_sock.bind(("0.0.0.0", 5000))
        self.discovery_sock.settimeout(0.1)
        
        # Data collection socket
        self.data_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.data_sock.bind(("0.0.0.0", 5001))
        self.data_sock.settimeout(0.1)
        
    def handle_discovery(self):
        """Handle node registration and role assignment"""
        try:
            data, addr = self.discovery_sock.recvfrom(1024)
            message = json.loads(data.decode())
            
            if message['type'] == 'REGISTER':
                ip = addr[0]
                node_info = message['node_info']
                
                # Register or update node
                if ip not in self.nodes:
                    role = 'MASTER' if len(self.nodes) == 0 else f'SENSOR_{len(self.nodes)}'
                    self.nodes[ip] = {
                        'role': role,
                        'sensors': node_info.get('sensors', []),
                        'last_seen': time.time(),
                        'data_history': [],
                        'status': 'ACTIVE'
                    }
                    print(f"Registered new node: {ip} as {role}")
                else:
                    self.nodes[ip]['last_seen'] = time.time()
                    self.nodes[ip]['status'] = 'ACTIVE'
                
                # Send back network topology
                response = {
                    'type': 'TOPOLOGY',
                    'your_role': self.nodes[ip]['role'],
                    'nodes': {ip: info['role'] for ip, info in self.nodes.items()},
                    'sequence': self.sequence_num
                }
                self.discovery_sock.sendto(json.dumps(response).encode(), addr)
                
        except (OSError, ValueError, KeyError):
            pass
    
    def handle_sensor_data(self):
        """Process incoming sensor data"""
        try:
            data, addr = self.data_sock.recvfrom(1024)
            message = json.loads(data.decode())
            
            if message['type'] == 'SENSOR_DATA':
                ip = addr[0]
                if ip in self.nodes:
                    # Store sensor data
                    sensor_data = {
                        'timestamp': time.time(),
                        'data': message['data'],
                        'node_id': message.get('node_id', ip)
                    }
                    
                    # Keep limited history
                    history = self.nodes[ip]['data_history']
                    history.append(sensor_data)
                    if len(history) > DATA_RETENTION:
                        history.pop(0)
                    
                    self.nodes[ip]['last_seen'] = time.time()
                    
                    # Check for alerts
                    self.check_alerts(ip, message['data'])
                    
                    # Send acknowledgment
                    ack = {
                        'type': 'DATA_ACK',
                        'sequence': message.get('sequence', 0),
                        'status': 'OK'
                    }
                    self.data_sock.sendto(json.dumps(ack).encode(), addr)
                    
                    print(f"Data from {ip}: {message['data']}")
                    
        except (OSError, ValueError, KeyError):
            pass
    
    def check_alerts(self, node_ip, data):
        """Check sensor data against thresholds"""
        for sensor, value in data.items():
            if sensor in ALERT_THRESHOLDS:
                thresholds = ALERT_THRESHOLDS[sensor]
                if value < thresholds['min'] or value > thresholds['max']:
                    alert = {
                        'timestamp': time.time(),
                        'node': node_ip,
                        'sensor': sensor,
                        'value': value,
                        'threshold': thresholds,
                        'severity': 'HIGH' if value < thresholds['min']*0.8 or value > thresholds['max']*1.2 else 'MEDIUM'
                    }
                    self.alerts.append(alert)
                    print(f"ALERT: {sensor} = {value} on node {node_ip}")
    
    def check_node_health(self):
        """Monitor node health and handle failures"""
        current_time = time.time()
        failed_nodes = []
        
        for ip, info in self.nodes.items():
            if current_time - info['last_seen'] > NODE_TIMEOUT:
                if info['status'] == 'ACTIVE':
                    info['status'] = 'FAILED'
                    failed_nodes.append(ip)
                    print(f"Node {ip} ({info['role']}) marked as FAILED")
        
        # Reassign roles if master failed
        if failed_nodes:
            self.reassign_roles()
    
    def reassign_roles(self):
        """Reassign roles when nodes fail"""
        active_nodes = [ip for ip, info in self.nodes.items() if info['status'] == 'ACTIVE']
        
        if active_nodes:
            # Assign new master if needed
            master_exists = any(info['role'] == 'MASTER' and info['status'] == 'ACTIVE' 
                              for info in self.nodes.values())
            
            if not master_exists:
                new_master = active_nodes[0]
                self.nodes[new_master]['role'] = 'MASTER'
                print(f"Promoted {new_master} to MASTER")
        
        self.sequence_num += 1
    
    def get_system_status(self):
        """Return comprehensive system status"""
        active_nodes = sum(1 for info in self.nodes.values() if info['status'] == 'ACTIVE')
        recent_alerts = [a for a in self.alerts if time.time() - a['timestamp'] < 300]  # last 5 min
        
        # Calculate averages from recent data
        all_recent_data = []
        for node_info in self.nodes.values():
            if node_info['data_history']:
                recent_data = [d for d in node_info['data_history'] if time.time() - d['timestamp'] < 300]
                all_recent_data.extend(recent_data)
        
        averages = {}
        if all_recent_data:
            sensor_values = {}
            for reading in all_recent_data:
                for sensor, value in reading['data'].items():
                    if sensor not in sensor_values:
                        sensor_values[sensor] = []
                    sensor_values[sensor].append(value)
            
            for sensor, values in sensor_values.items():
                averages[sensor] = sum(values) / len(values)
        
        return {
            'active_nodes': active_nodes,
            'total_nodes': len(self.nodes),
            'recent_alerts': len(recent_alerts),
            'system_averages': averages,
            'uptime': time.time()  # simplified
        }
    
    def run(self):
        """Main coordinator loop"""
        print("Environmental monitoring coordinator started")
        last_health_check = 0
        last_status_print = 0
        
        while True:
            current_time = time.time()
            
            # Handle incoming messages
            self.handle_discovery()
            self.handle_sensor_data()
            
            # Periodic health checks
            if current_time - last_health_check > 10:
                self.check_node_health()
                last_health_check = current_time
                gc.collect()  # Clean up memory
            
            # Status summary
            if current_time - last_status_print > 30:
                status = self.get_system_status()
                print(f"System: {status['active_nodes']}/{status['total_nodes']} nodes, "
                      f"{status['recent_alerts']} recent alerts")
                if status['system_averages']:
                    print(f"Averages: {status['system_averages']}")
                last_status_print = current_time
            
            time.sleep(0.1)

# Start the coordinator
if __name__ == "__main__":
    coordinator = EnvironmentalCoordinator()
    coordinator.run()
