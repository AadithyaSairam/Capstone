"""
ESP32 BLE Auto-Connection Module for ESP32 Nano
"""
import asyncio
from bleak import BleakScanner, BleakClient

class ESP32Bluetooth:
    def __init__(self, device_name="ESP32_Sensor"):
        self.device_name = device_name
        self.device_address = None
        self.client = None
        self.characteristic_uuid = "beb5483e-36e1-4688-b7f5-ea07361b26a8"
        self.data_callback = None
        
    async def discover_device(self):
        """Scan for ESP32 BLE device"""
        print(f"Scanning for '{self.device_name}'...")
        
        devices = await BleakScanner.discover(timeout=10.0)
        
        for device in devices:
            print(f"Found: {device.name} [{device.address}]")
            if device.name == self.device_name:
                self.device_address = device.address
                print(f"\n✓ Found target device at {device.address}")
                return True
        
        print(f"\n✗ Device '{self.device_name}' not found")
        return False
    
    async def connect(self):
        """Connect to ESP32 BLE device"""
        if not self.device_address:
            if not await self.discover_device():
                return False
        
        print(f"\nConnecting to {self.device_address}...")
        
        try:
            self.client = BleakClient(self.device_address)
            await self.client.connect()
            print("✓ Connected successfully!\n")
            return True
        except Exception as e:
            print(f"Connection failed: {e}")
            return False
    
    async def start_notifications(self, callback):
        """Start receiving notifications from ESP32"""
        if not self.client or not self.client.is_connected:
            print("Not connected!")
            return False
        
        try:
            await self.client.start_notify(self.characteristic_uuid, callback)
            return True
        except Exception as e:
            print(f"Failed to start notifications: {e}")
            return False
    
    async def disconnect(self):
        """Disconnect from ESP32"""
        if self.client and self.client.is_connected:
            await self.client.disconnect()
            print("Disconnected from ESP32")
