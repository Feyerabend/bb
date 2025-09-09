
# instrumentation for benchmarking game performance in python files
import time
import json
import gc

class PythonBenchmark:
    def __init__(self):
        self.frame_count = 0
        self.stats = {
            'frame_times': [],
            'collision_times': [],
            'render_times': [],
            'update_times': [],
            'collision_checks': [],
            'objects_rendered': [],
            'memory_usage': []
        }
        self.frame_start = 0
        self.report_interval = 60
        
    def frame_start(self):
        self.frame_start = time.perf_counter()
        self.collision_start = 0
        self.render_start = 0
        self.update_start = 0
        self.collision_checks = 0
        self.objects_rendered = 0
        
    def frame_end(self):
        frame_time = (time.perf_counter() - self.frame_start) * 1000  # ms
        self.stats['frame_times'].append(frame_time)
        self.frame_count += 1
        
        if self.frame_count % self.report_interval == 0:
            self.report_stats()
    
    def collision_start(self):
        self.collision_start = time.perf_counter()
        
    def collision_end(self):
        if self.collision_start:
            collision_time = (time.perf_counter() - self.collision_start) * 1000
            self.stats['collision_times'].append(collision_time)
    
    def render_start(self):
        self.render_start = time.perf_counter()
        
    def render_end(self):
        if self.render_start:
            render_time = (time.perf_counter() - self.render_start) * 1000
            self.stats['render_times'].append(render_time)
    
    def count_collision(self):
        self.collision_checks += 1
        
    def count_render_object(self):
        self.objects_rendered += 1
    
    def report_stats(self):
        if not self.stats['frame_times']:
            return
            
        # Get memory usage
        gc.collect()  # Force garbage collection for accurate measurement
        
        recent_frames = self.stats['frame_times'][-self.report_interval:]
        recent_collisions = self.stats['collision_times'][-self.report_interval:] if self.stats['collision_times'] else [0]
        recent_renders = self.stats['render_times'][-self.report_interval:] if self.stats['render_times'] else [0]
        
        avg_frame = sum(recent_frames) / len(recent_frames)
        avg_collision = sum(recent_collisions) / len(recent_collisions)
        avg_render = sum(recent_renders) / len(recent_renders)
        
        fps = 1000 / avg_frame if avg_frame > 0 else 0
        
        benchmark_data = {
            "benchmark": {
                "frame": self.frame_count,
                "timestamp": int(time.time() * 1000000),  # microseconds
                "frame_time_ms": recent_frames[-1] if recent_frames else 0,
                "avg_frame_time_ms": avg_frame,
                "min_frame_time_ms": min(recent_frames) if recent_frames else 0,
                "max_frame_time_ms": max(recent_frames) if recent_frames else 0,
                "collision_time_ms": recent_collisions[-1] if recent_collisions else 0,
                "avg_collision_time_ms": avg_collision,
                "render_time_ms": recent_renders[-1] if recent_renders else 0,
                "avg_render_time_ms": avg_render,
                "fps": fps,
                "collision_checks": self.collision_checks,
                "objects_rendered": self.objects_rendered,
                "active_bullets": len([b for b in bullets if b.get('active', True)]),
                "active_bombs": len([b for b in bombs if b.get('active', True)]),
                "alive_invaders": len([i for i in invaders if i.get('alive', True)])
            }
        }
        
        print(json.dumps(benchmark_data))

# Global benchmark instance
benchmark = PythonBenchmark()

# Add these calls to your main game loop:
# benchmark.frame_start()    # at start of loop
# benchmark.collision_start() # before collision detection  
# benchmark.collision_end()   # after collision detection
# benchmark.render_start()    # before rendering
# benchmark.render_end()      # after rendering  
# benchmark.frame_end()       # at end of loop

# In collision detection, add: benchmark.count_collision()
# When rendering objects, add: benchmark.count_render_object()


// ============================================================================
// DATA COLLECTION SCRIPT - RUN ON YOUR COMPUTER
// ============================================================================

/*
Python script to collect data from Pico via serial:

#!/usr/bin/env python3
import serial
import json
import time
import csv
from collections import defaultdict
import matplotlib.pyplot as plt

class BenchmarkCollector:
    def __init__(self, serial_port, baud_rate=115200):
        self.serial_port = serial_port
        self.baud_rate = baud_rate
        self.data = defaultdict(list)
        
    def collect_data(self, duration_seconds=60):
        print(f"Collecting data from {self.serial_port} for {duration_seconds} seconds...")
        
        with serial.Serial(self.serial_port, self.baud_rate, timeout=1) as ser:
            start_time = time.time()
            
            while time.time() - start_time < duration_seconds:
                try:
                    line = ser.readline().decode('utf-8').strip()
                    if line.startswith('{"benchmark":'):
                        data = json.loads(line)
                        benchmark = data['benchmark']
                        
                        # Store all metrics
                        for key, value in benchmark.items():
                            self.data[key].append(value)
                        
                        # Print progress
                        if 'frame' in benchmark:
                            print(f"Frame {benchmark['frame']}: {benchmark.get('fps', 0):.1f} FPS")
                            
                except (json.JSONDecodeError, UnicodeDecodeError):
                    continue
                except KeyboardInterrupt:
                    break
        
        print("Data collection complete!")
        return self.data
    
    def save_results(self, filename):
        with open(filename, 'w', newline='') as csvfile:
            if not self.data:
                return
                
            fieldnames = list(self.data.keys())
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            # Write rows (assuming all lists are same length)
            max_length = max(len(values) for values in self.data.values())
            for i in range(max_length):
                row = {}
                for key, values in self.data.items():
                    row[key] = values[i] if i < len(values) else None
                writer.writerow(row)
        
        print(f"Results saved to {filename}")

# Usage:
# collector = BenchmarkCollector("/dev/ttyACM0")  # Linux
# collector = BenchmarkCollector("COM3")          # Windows  
# data = collector.collect_data(60)  # 60 seconds
# collector.save_results("benchmark_results.csv")
