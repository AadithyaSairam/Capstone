import serial
import time

try:
    print("Attempting to connect to COM4...")
    ser = serial.Serial('COM4', 9600, timeout=1) #SET CORRECT COM PORT
    time.sleep(2)  # Wait for Arduino to reset
    print("✓ Arduino connected successfully!")
    
    # Test read
    for i in range(5):
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').strip()
            print(f"Received: {line}")
        time.sleep(0.5)
    
except serial.SerialException as e:
    print(f"✗ Serial Error: {e}")
    print("Troubleshooting:")
    print("  1. Close Arduino IDE Serial Monitor")
    print("  2. Check COM4 in Device Manager")
    print("  3. Try unplugging/replugging Arduino")
    ser = None
except Exception as e:
    print(f"✗ Unexpected error: {e}")
    ser = None
