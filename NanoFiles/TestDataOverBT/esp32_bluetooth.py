"""
ESP32 Bluetooth Auto-Connection Module
Automatically discovers and connects to ESP32
"""
import bluetooth
import time

class ESP32Bluetooth:
    def __init__(self, device_name="ESP32_Sensor"):
        self.device_name = device_name
        self.target_address = None
        self.socket = None
        
    def discover_device(self):
        """Scan for ESP32 Bluetooth device"""
        print(f"Scanning for '{self.device_name}'...")
        
        try:
            nearby_devices = bluetooth.discover_devices(duration=8, lookup_names=True, flush_cache=True)
            
            for addr, name in nearby_devices:
                print(f"Found: {name} [{addr}]")
                if name == self.device_name:
                    self.target_address = addr
                    print(f"\n✓ Found target device: {name} at {addr}")
                    return True
            
            print(f"\n✗ Device '{self.device_name}' not found")
            return False
            
        except Exception as e:
            print(f"Discovery error: {e}")
            return False
    
    def connect(self):
        """Automatically discover and connect to ESP32"""
        if not self.target_address:
            if not self.discover_device():
                print("Please make sure:")
                print("1. ESP32 is powered on")
                print("2. Bluetooth is enabled on your PC")
                print("3. Device name matches in both ESP32 and Python code")
                return False
        
        print(f"\nConnecting to {self.target_address}...")
        
        try:
            self.socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
            self.socket.connect((self.target_address, 1))  # Port 1 for RFCOMM
            print("✓ Connected successfully!\n")
            return True
            
        except Exception as e:
            print(f"Connection failed: {e}")
            self.socket = None
            return False
    
    def receive_data(self):
        """Receive data from ESP32"""
        if not self.socket:
            print("Not connected!")
            return None
        
        try:
            data = self.socket.recv(1024).decode('utf-8').strip()
            return data
        except Exception as e:
            print(f"Receive error: {e}")
            return None
    
    def disconnect(self):
        """Close Bluetooth connection"""
        if self.socket:
            self.socket.close()
            print("Disconnected from ESP32")
