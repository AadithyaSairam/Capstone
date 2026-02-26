"""
ESP32 BLE Auto-Connection Module with data callback and write capability
"""
import asyncio
from bleak import BleakScanner, BleakClient
import threading


class ESP32Bluetooth:
    def __init__(self, device_name="ESP32_Sensor"):
        self.device_name = device_name
        self.device_address = None
        self.client = None
        self.characteristic_uuid = "beb5483e-36e1-4688-b7f5-ea07361b26a8"
        self.data_callback = None
        self.latest_data = None
        self.connected = False
        self.loop = None
        
    async def discover_device(self):
        """Scan for ESP32 BLE device"""
        print(f"Scanning for '{self.device_name}'...")
        
        devices = await BleakScanner.discover(timeout=10.0)
        
        for device in devices:
            if device.name == self.device_name:
                self.device_address = device.address
                print(f"✓ Found device at {device.address}")
                return True
        
        print(f"✗ Device '{self.device_name}' not found")
        return False
    
    async def connect(self):
        """Connect to ESP32 BLE device"""
        if not self.device_address:
            if not await self.discover_device():
                return False
        
        print(f"Connecting to {self.device_address}...")
        
        try:
            self.client = BleakClient(self.device_address)
            await self.client.connect()
            self.connected = True
            print("✓ Connected successfully!\n")
            return True
        except Exception as e:
            print(f"Connection failed: {e}")
            return False
    
    def notification_handler(self, sender, data):
        """Internal handler for BLE notifications"""
        try:
            raw_data = data.decode('utf-8').strip()
            self.latest_data = raw_data
            if self.data_callback:
                self.data_callback(raw_data)
        except Exception as e:
            print(f"Notification error: {e}")
    
    async def start_notifications(self, callback=None):
        """Start receiving notifications from ESP32"""
        if not self.client or not self.client.is_connected:
            print("Not connected!")
            return False
        
        self.data_callback = callback
        
        try:
            await self.client.start_notify(self.characteristic_uuid, self.notification_handler)
            return True
        except Exception as e:
            print(f"Failed to start notifications: {e}")
            return False
    
    async def write_command(self, command):
        """Write a command to ESP32"""
        if not self.client or not self.client.is_connected:
            print("Cannot write: Not connected!")
            return False
        
        try:
            await self.client.write_gatt_char(self.characteristic_uuid, command.encode())
            return True
        except Exception as e:
            print(f"Write failed: {e}")
            return False
    
    async def run_loop(self, callback=None):
        """Connect and run notification loop"""
        self.loop = asyncio.get_running_loop()
        
        if not await self.connect():
            return
        
        if not await self.start_notifications(callback):
            await self.disconnect()
            return
        
        # Keep running
        try:
            while self.connected:
                await asyncio.sleep(0.1)
        except Exception as e:
            print(f"Loop error: {e}")
        finally:
            await self.disconnect()
    
    async def disconnect(self):
        """Disconnect from ESP32"""
        self.connected = False
        if self.client and self.client.is_connected:
            await self.client.disconnect()
            print("Disconnected from ESP32")
    
    def get_latest_data(self):
        """Get the most recent data received"""
        return self.latest_data


# Global instance for thread-safe command sending
_esp32_instance = None

def run_bluetooth_thread(device_name, data_callback):
    """Helper function to run BLE in a separate thread"""
    global _esp32_instance
    _esp32_instance = ESP32Bluetooth(device_name)
    asyncio.run(_esp32_instance.run_loop(data_callback))


def send_command_sync(command):
    """Send command to ESP32 from main thread (thread-safe)"""
    global _esp32_instance
    
    if not _esp32_instance or not _esp32_instance.connected:
        return False
    
    # Create new event loop for this thread
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        result = loop.run_until_complete(_esp32_instance.write_command(command))
        return result
    except Exception as e:
        print(f"Command send error: {e}")
        return False
    finally:
        loop.close()
