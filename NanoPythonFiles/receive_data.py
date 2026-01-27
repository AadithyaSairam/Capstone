"""
ESP32 Data Receiver
Receives and processes sensor data from ESP32
"""
import socket
from esp32_network import ESP32Network

# Configuration
ESP32_IP = "192.168.4.1"
ESP32_PORT = 80

def process_data(raw_data):
    """Parse and process incoming CSV data"""
    try:
        values = raw_data.split(',')
        if len(values) == 3:
            timestamp = values[0]
            sensor1 = float(values[1])
            sensor2 = float(values[2])
            
            # Process your data here
            print(f"Timestamp: {timestamp}ms | Sensor1: {sensor1:.2f} | Sensor2: {sensor2:.2f}")
            
            # Example: Save to file, trigger alerts, etc.
            # if sensor1 > 5.0:
            #     print("  WARNING: Sensor1 threshold exceeded!")
            
            return {
                'timestamp': timestamp,
                'sensor1': sensor1,
                'sensor2': sensor2
            }
    except Exception as e:
        print(f"Error processing data: {e}")
        return None

def receive_data():
    """Connect to ESP32 and receive data stream"""
    try:
        # Create TCP client
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((ESP32_IP, ESP32_PORT))
        print(f"Connected to ESP32 at {ESP32_IP}:{ESP32_PORT}\n")
        
        data_buffer = ""
        
        while True:
            # Receive data
            chunk = client.recv(1024).decode('utf-8')
            
            if not chunk:
                print("Connection closed by ESP32")
                break
            
            # Handle partial receives
            data_buffer += chunk
            
            # Process complete lines
            while '\n' in data_buffer:
                line, data_buffer = data_buffer.split('\n', 1)
                line = line.strip()
                
                if line:
                    process_data(line)
                    
    except KeyboardInterrupt:
        print("\n\nStopping data reception...")
    except Exception as e:
        print(f"Connection error: {e}")
    finally:
        client.close()
        print("Connection closed")

if __name__ == "__main__":
    # Step 1: Connect to ESP32 network
    esp32 = ESP32Network(ssid="ESP32_TestNet", password="12345678")
    esp32.connect()
    
    print("\n" + "="*50)
    print("Starting data reception...")
    print("="*50 + "\n")
    
    # Step 2: Receive data
    receive_data()
    
    # Optional: Disconnect when done
    # esp32.disconnect()
