# UNTESTED
# Enhanced TDOS
import gc
import micropython

class MemoryOptimizedMessage:
    __slots__ = ('version', 'msg_type', 'msg_id', 'payload', 'timestamp', 'reply_to')
    
    def __init__(self, msg_type, payload, msg_id=None, reply_to=None):
        self.version = 1
        self.msg_type = msg_type
        self.msg_id = msg_id or self._generate_id()
        self.payload = payload
        self.timestamp = time.ticks_ms()
        self.reply_to = reply_to
    
    @staticmethod
    @micropython.native
    def _generate_id():
        return hex(time.ticks_us() ^ machine.unique_id()[0])[2:10]
    
    def serialize(self):
        import ujson
        data = {
            "v": self.version,
            "t": self.msg_type,
            "id": self.msg_id,
            "ts": self.timestamp,
            "p": self.payload
        }
        if self.reply_to:
            data["r"] = self.reply_to
        
        return ujson.dumps(data).encode()
    
    @classmethod
    def deserialize(cls, data):
        import ujson
        try:
            msg_dict = ujson.loads(data.decode())
            return cls(
                msg_type=msg_dict["t"],
                payload=msg_dict["p"],
                msg_id=msg_dict["id"],
                reply_to=msg_dict.get("r")
            )
        except Exception as e:
            gc.collect()
            raise ValueError(f"Deserialize failed: {e}")



import uasyncio as asyncio

class AsyncSensorNode:
    def __init__(self, service_name, sensor_pin=None):
        self.service_name = service_name
        self.sensor_pin = sensor_pin
        self.running = True
        self.socket = None
        self.message_queue = []
        
    async def setup_async_socket(self):
        import socket
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(("", 5000))
        self.socket.setblocking(False)  # critical for async
        
    async def handle_requests(self):
        """Async request handler"""
        while self.running:
            try:
                data, addr = self.socket.recvfrom(1024)
                if data:
                    asyncio.create_task(self.process_request(data, addr))
                    
            except OSError:
                await asyncio.sleep_ms(10)
            except Exception as e:
                print(f"Request handler error: {e}")
                await asyncio.sleep_ms(100)
    
    async def process_request(self, data, addr):
        try:
            msg = MemoryOptimizedMessage.deserialize(data)
            response = await self.handle_sensor_read(msg)
            self.socket.sendto(response.serialize(), addr)
        except Exception as e:
            error_resp = MemoryOptimizedMessage(
                MessageType.ERROR,
                {"error": str(e)},
                reply_to=msg.msg_id if 'msg' in locals() else None
            )
            self.socket.sendto(error_resp.serialize(), addr)
    
    async def send_heartbeat(self):
        backoff = 1
        while self.running:
            try:
                # Heartbeat logic here
                backoff = 1  # Reset on success
                await asyncio.sleep(5)
            except Exception as e:
                print(f"Heartbeat failed: {e}")
                await asyncio.sleep(min(backoff * 2, 30))  # Exponential backoff
                backoff *= 2
    
    async def run_async(self):
        await self.setup_async_socket()
        
        # Start concurrent tasks
        tasks = [
            asyncio.create_task(self.handle_requests()),
            asyncio.create_task(self.send_heartbeat()),
        ]
        
        try:
            await asyncio.gather(*tasks)
        except KeyboardInterrupt:
            print("Shutting down...")
        finally:
            await self.cleanup_async()
    
    async def cleanup_async(self):
        self.running = False
        if self.socket:
            self.socket.close()


import machine

class PowerManager:
    def __init__(self):
        self.sleep_modes = {
            'active': 0,
            'light_sleep': 1,
            'deep_sleep': 2
        }
        self.current_mode = 'active'
        self.wake_pin = machine.Pin(0, machine.Pin.IN, machine.Pin.PULL_UP)
    
    def enter_light_sleep(self, duration_ms):
        print(f"Entering light sleep for {duration_ms}ms")
        machine.lightsleep(duration_ms)
    
    def enter_deep_sleep(self, duration_ms):
        print(f"Entering deep sleep for {duration_ms}ms")
        machine.deepsleep(duration_ms)
    
    def adaptive_sleep(self, activity_level):
        if activity_level < 0.1:  # Very low activity
            self.enter_light_sleep(1000)
        elif activity_level < 0.05:  # Almost no activity
            self.enter_deep_sleep(5000)



import sys

class CircuitBreaker:
    def __init__(self, failure_threshold=5, timeout=30):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = 0
        self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN
    
    def call(self, func, *args, **kwargs):
        if self.state == 'OPEN':
            if time.ticks_diff(time.ticks_ms(), self.last_failure_time) > self.timeout * 1000:
                self.state = 'HALF_OPEN'
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = func(*args, **kwargs)
            if self.state == 'HALF_OPEN':
                self.state = 'CLOSED'
                self.failure_count = 0
            return result
            
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.ticks_ms()
            
            if self.failure_count >= self.failure_threshold:
                self.state = 'OPEN'
                
            raise e

class ResilientServiceRegistry:
    def __init__(self):
        self.services = {}
        self.circuit_breakers = {}
        self.backup_services = {}  # Fallback services
        
    def register_service(self, name, ip, port, metadata=None, is_backup=False):
        service_info = {
            "ip": ip,
            "port": port,
            "last_seen": time.ticks_ms(),
            "metadata": metadata or {},
            "failures": 0,
            "success_rate": 1.0
        }
        
        if is_backup:
            if name not in self.backup_services:
                self.backup_services[name] = []
            self.backup_services[name].append(service_info)
        else:
            self.services[name] = service_info
            self.circuit_breakers[name] = CircuitBreaker()
    
    def get_service_with_fallback(self, name):
        # Try primary service
        if name in self.services:
            try:
                service = self.services[name]
                if self.circuit_breakers[name].state != 'OPEN':
                    return service
            except:
                pass
        
        # Try backup services
        if name in self.backup_services:
            for backup in self.backup_services[name]:
                if time.ticks_diff(time.ticks_ms(), backup["last_seen"]) < 30000:
                    return backup
        
        return None



import json

class ConfigManager:
    def __init__(self, config_file='tdos_config.json'):
        self.config_file = config_file
        self.config = self.load_config()
    
    def load_config(self):
        default_config = {
            "network": {
                "ssid": "TDOS",
                "password": "12345678",
                "retry_attempts": 3,
                "connection_timeout": 10
            },
            "discovery": {
                "port": 4000,
                "heartbeat_interval": 5,
                "service_timeout": 15
            },
            "power": {
                "enable_sleep": True,
                "sleep_threshold": 0.1,
                "max_sleep_duration": 5000
            },
            "logging": {
                "level": "INFO",
                "max_log_size": 10240,
                "enable_file_logging": True
            }
        }
        
        try:
            with open(self.config_file, 'r') as f:
                user_config = json.load(f)
                # Merge with defaults
                return self.merge_configs(default_config, user_config)
        except:
            print("Using default configuration")
            return default_config
    
    def merge_configs(self, default, user):
        result = default.copy()
        for key, value in user.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self.merge_configs(result[key], value)
            else:
                result[key] = value
        return result
    
    def save_config(self):
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f)
        except Exception as e:
            print(f"Failed to save config: {e}")
    
    def get(self, key_path, default=None):
        keys = key_path.split('.')
        value = self.config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value



import time
import os

class Logger:
    LEVELS = {'DEBUG': 0, 'INFO': 1, 'WARN': 2, 'ERROR': 3, 'CRITICAL': 4}
    
    def __init__(self, level='INFO', max_size=10240):
        self.level = self.LEVELS.get(level, 1)
        self.max_size = max_size
        self.log_file = 'tdos.log'
        
    def log(self, level, message, **kwargs):
        if self.LEVELS.get(level, 0) >= self.level:
            timestamp = time.localtime()
            log_entry = {
                'timestamp': f"{timestamp[0]}-{timestamp[1]:02d}-{timestamp[2]:02d} {timestamp[3]:02d}:{timestamp[4]:02d}:{timestamp[5]:02d}",
                'level': level,
                'message': message,
                **kwargs
            }
            
            # Console output
            print(f"[{log_entry['timestamp']}] {level}: {message}")
            
            # File logging with rotation
            self._write_to_file(log_entry)
    
    def _write_to_file(self, entry):
        try:
            # Simple log rotation
            try:
                stat = os.stat(self.log_file)
                if stat[6] > self.max_size:  # File size
                    os.rename(self.log_file, f"{self.log_file}.old")
            except:
                pass  # File doesn't exist yet
            
            with open(self.log_file, 'a') as f:
                f.write(json.dumps(entry) + '\n')
                
        except Exception as e:
            print(f"Logging error: {e}")
    
    def debug(self, message, **kwargs):
        self.log('DEBUG', message, **kwargs)
    
    def info(self, message, **kwargs):
        self.log('INFO', message, **kwargs)
    
    def warn(self, message, **kwargs):
        self.log('WARN', message, **kwargs)
    
    def error(self, message, **kwargs):
        self.log('ERROR', message, **kwargs)




import network

class NetworkManager:
    def __init__(self, config):
        self.config = config
        self.wlan = network.WLAN(network.STA_IF)
        self.connection_callbacks = []
        
    def add_connection_callback(self, callback):
        self.connection_callbacks.append(callback)
    
    def connect_with_retry(self):
        self.wlan.active(True)
        
        for attempt in range(self.config.get('network.retry_attempts', 3)):
            if self.wlan.isconnected():
                ip = self.wlan.ifconfig()[0]
                self._notify_callbacks('connected', ip)
                return ip
            
            try:
                print(f"Connection attempt {attempt + 1}")
                self.wlan.connect(
                    self.config.get('network.ssid'),
                    self.config.get('network.password')
                )
                
                # Wait with timeout
                timeout = self.config.get('network.connection_timeout', 10)
                start = time.ticks_ms()
                
                while not self.wlan.isconnected() and time.ticks_diff(time.ticks_ms(), start) < timeout * 1000:
                    time.sleep_ms(100)
                
                if self.wlan.isconnected():
                    ip = self.wlan.ifconfig()[0]
                    self._notify_callbacks('connected', ip)
                    return ip
                    
            except Exception as e:
                print(f"Connection failed: {e}")
            
            # Exponential backoff between attempts
            time.sleep(min(2 ** attempt, 16))
        
        self._notify_callbacks('failed', None)
        raise RuntimeError("Failed to connect after all retry attempts")
    
    def _notify_callbacks(self, event, data):
        for callback in self.connection_callbacks:
            try:
                callback(event, data)
            except Exception as e:
                print(f"Callback error: {e}")
    
    async def monitor_connection(self):
        while True:
            if not self.wlan.isconnected():
                print("Connection lost, attempting reconnection...")
                try:
                    self.connect_with_retry()
                except Exception as e:
                    print(f"Reconnection failed: {e}")
                    await asyncio.sleep(30)  # Wait before retry
            
            await asyncio.sleep(10)  # every 10 seconds

