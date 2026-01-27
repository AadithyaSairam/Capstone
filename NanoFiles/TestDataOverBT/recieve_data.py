"""
ESP32 BLE Data Receiver
"""
import asyncio
from esp32_bluetooth import ESP32Bluetooth

def process_data(raw_data):
    """Parse and process CSV data"""
    try:
        values = raw_data.split(',')
        if len(values) == 3:
            timestamp = values[0]
            sensor1 = float(values[1])
            sensor2 = float(values[2])
            
            print(f"Timestamp: {timestamp}ms | Sensor1: {sensor1:.2f} | Sensor2: {sensor2:.2f}")
            
            return {
                'timestamp': timestamp,
                'sensor1': sensor1,
                'sensor2': sensor2
            }
    except Exception as e:
        print(f"Parse error: {e}")
        return None

def notification_handler(sender, data):
    """Callback for BLE notifications"""
    raw_data = data.decode('utf-8').strip()
    process_data(raw_data)

async def main():
    print("="*60)
    print("ESP32 BLE Data Receiver")
    print("="*60 + "\n")
    
    esp32 = ESP32Bluetooth(device_name="ESP32_Sensor")
    
    # Connect
    if not await esp32.connect():
        print("\nFailed to connect. Exiting...")
        return
    
    # Start receiving notifications
    if not await esp32.start_notifications(notification_handler):
        print("\nFailed to start notifications. Exiting...")
        await esp32.disconnect()
        return
    
    print("Receiving data (Press Ctrl+C to stop)...\n")
    
    try:
        # Keep running
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("\n\nStopping...")
    finally:
        await esp32.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
