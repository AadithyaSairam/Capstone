import pyvista as pv
import numpy as np
import matplotlib.pyplot as plt
import serial
import time
from serial.tools import list_ports

# === CALIBRATION SETUP ===
cal_true = np.array([0, 1, 2])
cal_sensor = np.array([35000, -20000, -75000])
coeffs = np.polyfit(cal_sensor, cal_true, 1)
cal_slope, cal_intercept = coeffs[0], coeffs[1]

def sensor_to_pressure(sensor_value, clamp=True):
    """Convert raw sensor bits to pressure value (0-2 range)"""
    if sensor_value == 0:
        return 0.0
    pressure = cal_slope * sensor_value + cal_intercept
    if clamp:
        pressure = np.clip(pressure, 0, 2)
    return pressure

# === OUTLIER FILTER ===
class PressureFilter:
    def __init__(self, max_jump=0.5, window_size=3):
        self.max_jump = max_jump
        self.window_size = window_size
        self.history = []
        
    def filter(self, new_reading):
        if len(self.history) == 0:
            self.history.append(new_reading)
            return new_reading
        
        last_reading = self.history[-1]
        filtered_reading = []
        
        for i in range(4):
            change = abs(new_reading[i] - last_reading[i])
            if change > self.max_jump:
                filtered_reading.append(last_reading[i])
            else:
                filtered_reading.append(new_reading[i])
        
        self.history.append(filtered_reading)
        if len(self.history) > self.window_size:
            self.history.pop(0)
        
        return filtered_reading

pressure_filter = PressureFilter(max_jump=0.5, window_size=3)

# === ARDUINO CONNECTION ===
def find_arduino_port(baudrate=9600, timeout=1):
    """Automatically find Arduino COM port"""
    ports = list(list_ports.comports())
    
    if not ports:
        print("No serial ports found")
        return None
    
    print("Available ports:")
    for port in ports:
        print(f"  {port.device} - {port.description}")
    
    for port in ports:
        desc = port.description.lower()
        if any(x in desc for x in ["arduino", "ch340", "usb serial", "cp210", "ftdi"]):
            try:
                ser = serial.Serial(port.device, baudrate, timeout=timeout)
                time.sleep(2)
                print(f"Connected to Arduino on {port.device}")
                return ser
            except:
                pass
    
    print("No usable Arduino found")
    return None

ser = find_arduino_port()

if ser is None:
    print("Warning: Arduino not found, using simulated data")
else:
    ser.reset_input_buffer()
    time.sleep(0.5)
    print("Serial buffer flushed")

# === LOAD 3D MODEL ===
mesh = pv.read('leg.stl')
cell_centers = mesh.cell_centers().points

patch_centers = [
    [79.22101593, 12.75070763, 155.10850525],
    [28.12449265, 48.21684265, 159.52259827],
    [76.4567337, 108.86454773, 137.45446777],
    [118.10018921, 54.5916481, 130.84025574],
]

patch_radius = 15.0
region_ids = np.full(mesh.n_cells, -1)
for region_idx, center in enumerate(patch_centers):
    distances = np.linalg.norm(cell_centers - center, axis=1)
    within_radius = distances < patch_radius
    region_ids[within_radius] = region_idx

mesh['region'] = region_ids
max_pressure = 2.0

def get_color_from_pressure(intensity):
    intensity = np.clip(intensity, 0, 1)
    colormap = plt.get_cmap('jet')
    rgba = colormap(intensity)
    return rgba[:3]

def update_mesh_colors(pressure_values):
    colors = np.zeros((mesh.n_cells, 3))
    colors[:] = [0.8, 0.8, 0.8]
    
    for i in range(4):
        mask = mesh['region'] == i
        if np.any(mask):
            intensity = pressure_values[i] / max_pressure
            color = get_color_from_pressure(intensity)
            colors[mask] = color
    
    return colors

# === SERIAL READING ===
time_step = 0
last_valid_reading = [1.0, 1.0, 1.0, 1.0]
step_counter = 0

def read_arduino_pressure():
    """Read pressure values from Arduino with outlier filtering"""
    global time_step
    
    if ser:
        try:
            line = ser.readline().decode('utf-8').strip()
            
            if not line or ',' not in line:
                return None
            
            raw_values = [float(x) for x in line.split(',')]
            
            if len(raw_values) != 4:
                return None
            
            calibrated = [sensor_to_pressure(v) for v in raw_values]
            filtered = pressure_filter.filter(calibrated)
            
            return filtered
            
        except Exception as e:
            print(f"Error: {e}")
            return None
    
    # Fallback to simulated data
    time_step += 0.1
    p1 = 1.0 + 0.6 * np.sin(time_step)
    p2 = 1.0 + 0.6 * np.sin(time_step + np.pi/2)
    p3 = 1.0 + 0.6 * np.sin(time_step + np.pi)
    p4 = 1.0 + 0.6 * np.sin(time_step + 3*np.pi/2)
    return [p1, p2, p3, p4]

# === CREATE PLOTTER ===
plotter = pv.Plotter()

# Add initial mesh
initial_pressures = [1.0, 1.0, 1.0, 1.0]
initial_colors = update_mesh_colors(initial_pressures)
mesh.cell_data['RGB'] = (initial_colors * 255).astype(np.uint8)
actor = plotter.add_mesh(mesh, scalars='RGB', rgb=True, 
                        show_edges=False, lighting=True)

# === TIMER CALLBACK (NON-BLOCKING) ===
def update_callback(step):
    """Called by timer - updates visualization without blocking"""
    global last_valid_reading, step_counter
    
    # Read new pressure data
    pressure_values = read_arduino_pressure()
    
    if pressure_values is None:
        pressure_values = last_valid_reading
    else:
        last_valid_reading = pressure_values
    
    # Update colors
    new_colors = update_mesh_colors(pressure_values)
    rgb_colors = (new_colors * 255).astype(np.uint8)
    mesh.cell_data['RGB'] = rgb_colors
    
    # Print values
    print(f"Step {step_counter}: P1={pressure_values[0]:.1f} P2={pressure_values[1]:.1f} "
          f"P3={pressure_values[2]:.1f} P4={pressure_values[3]:.1f}")
    
    step_counter += 1

# Add timer event (100ms = 10Hz update rate)
plotter.add_timer_event(max_steps=5000, duration=100, callback=update_callback)

# Show plot (this will be interactive and non-blocking within VTK event loop)
print("Starting animation... Close the window to stop.")
print("You can now interact with the plot (rotate, zoom, pan)")
plotter.show()

# Cleanup
if ser:
    ser.close()
