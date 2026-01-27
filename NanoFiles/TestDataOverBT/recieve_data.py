"""
ESP32 Bluetooth Data Receiver
Automatically connects and receives sensor data
"""
from esp32_bluetooth import ESP32Bluetooth
import time

def process_data(raw_data):
    """Parse and process CSV data"""
    try:
        values = raw_data.split(',')
        if len(values) == 3:
            timestamp = values[0]
            sensor1 = float(values[1])
            sensor2 = float(values[2])
            
            print(f"Timestamp: {timestamp}ms | Sensor1: {sensor1:.2f} | Sensor2: {sensor2:.2f}")
            
            # Add your custom processing here
            # Example: Save to file, trigger alerts, etc.
            
            return {
                'timestamp': timestamp,
                'sensor1': sensor1,
                'sensor2': sensor2
            }
    except Exception as e:
        print(f"Parse error: {e}")
        return None

def main():
    print("="*60)
    print("ESP32 Bluetooth Data Receiver")
    print("="*60 + "\n")
    
    # Create Bluetooth connection object
    esp32 = ESP32Bluetooth(device_name="ESP32_Sensor")
    
    # Auto-discover and connect
    if not esp32.connect():
        print("\nFailed to connect. Exiting...")
        return
    
    print("Receiving data (Press Ctrl+C to stop)...\n")
    
    data_buffer = ""
    
    try:
        while True:
            # Receive data
            chunk = esp32.receive_data()
            
            if chunk:
                data_buffer += chunk
                
                # Process complete lines
                while '\n' in data_buffer:
                    line, data_buffer = data_buffer.split('\n', 1)
                    line = line.strip()
                    
                    if line:
                        process_data(line)
            else:
                time.sleep(0.1)  # Brief pause if no data
                
    except KeyboardInterrupt:
        print("\n\nStopping data reception...")
    except Exception as e:
        print(f"\nError: {e}")
    finally:
        esp32.disconnect()

if __name__ == "__main__":
    main()
