import serial
import serial.tools.list_ports
import threading
import time

_ser = None
_thread = None
_running = False

def _find_port():
    ports = serial.tools.list_ports.comports()
    for p in ports:
        desc = p.device.lower() + " " + p.description.lower()
        if any(x in desc for x in ["usbmodem", "ttyusb", "ttyacm", "cu.usbmodem",
                                    "ch340", "cp210", "uart", "com"]):
            return p.device
    return None

def _parse(line: str):
    """Parse '0,p1,p2,p3,p4' → [p1, p2, p3, p4] floats, or None on error."""
    try:
        parts = line.strip().split(",")
        if len(parts) == 5:
            return [float(p) for p in parts[1:]]
    except (ValueError, IndexError):
        pass
    return None

def run_bluetooth_thread(device_name, data_callback):
    """
    Drop-in replacement for esp32_bluetooth.run_bluetooth_thread().
    device_name is ignored (auto-detects port). data_callback([p1,p2,p3,p4]).
    """
    global _ser, _thread, _running

    port = _find_port()
    if not port:
        print("✗ No serial port found — check USB cable")
        return

    print(f"✓ Serial port found: {port}")

    def _read_loop():
        global _ser, _running
        try:
            _ser = serial.Serial(port, 115200, timeout=1)
            time.sleep(1.5)   # wait for Arduino reset after DTR toggle
            _ser.reset_input_buffer()
            print(f"✓ Serial connected on {port}")
            _running = True
            while _running:
                try:
                    raw = _ser.readline().decode("utf-8", errors="ignore")
                    values = _parse(raw)
                    if values is not None:
                        data_callback(values)
                except Exception as e:
                    print(f"Serial read error: {e}")
                    time.sleep(0.1)
        except serial.SerialException as e:
            print(f"Serial open error: {e}")
        finally:
            if _ser and _ser.is_open:
                _ser.close()

    _thread = threading.Thread(target=_read_loop, daemon=True)
    _thread.start()

def send_command(cmd: str):
    """Send a text command to the Arduino (e.g. 'TARE')."""
    global _ser
    if _ser and _ser.is_open:
        try:
            _ser.write((cmd + "\n").encode("utf-8"))
        except Exception as e:
            print(f"Serial write error: {e}")

def is_connected() -> bool:
    return _ser is not None and _ser.is_open and _running

def stop():
    global _running
    _running = False
