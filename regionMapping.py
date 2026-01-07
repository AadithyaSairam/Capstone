import pyvista as pv
import numpy as np
import matplotlib.pyplot as plt
import serial
import time
from serial.tools import list_ports


def find_arduino_port(baudrate=9600, timeout=1):
    """Automatically find Arduino COM port"""
    ports = list(list_ports.comports())

    if not ports:
        print("No serial ports found")
        return None

    print("Available ports:")
    for port in ports:
        print(f"  {port.device} - {port.description}")

    # First: try ports that look like Arduino
    for port in ports:
        desc = port.description.lower()
        print(desc)
        print(any(x in desc for x in ["arduino", "ch340", "usb serial", "cp210", "ftdi"]))
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


# === SETUP SERIAL CONNECTION ===
ser = find_arduino_port()

if ser is None:
    print("Warning: Arduino not found, using simulated data")

# Load your 3D leg model
mesh = pv.read('leg.stl')

# Get cell centers
cell_centers = mesh.cell_centers().points

# YOUR 4 picked sensor locations
patch_centers = [
    [79.22101593, 12.75070763, 155.10850525],
    [28.12449265, 48.21684265, 159.52259827],
    [76.4567337, 108.86454773, 137.45446777],
    [118.10018921, 54.5916481, 130.84025574],
]

patch_radius = 15.0

# Assign regions
region_ids = np.full(mesh.n_cells, -1)
for region_idx, center in enumerate(patch_centers):
    distances = np.linalg.norm(cell_centers - center, axis=1)
    within_radius = distances < patch_radius
    region_ids[within_radius] = region_idx

mesh['region'] = region_ids
max_pressure = 100.0

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

# Create plotter with interactive update enabled
plotter = pv.Plotter()

# Add initial mesh
initial_pressures = [20, 40, 60, 80]
mesh.cell_data['colors'] = update_mesh_colors(initial_pressures)
actor = plotter.add_mesh(mesh, scalars='colors', rgb=True, 
                        show_edges=False, lighting=True)

# Show with interactive update
plotter.show(interactive_update=True, auto_close=False)

# === READ FROM ARDUINO ===
time_step = 0

def read_arduino_pressure():
    """Read pressure values from Arduino"""
    global time_step
    
    if ser and ser.in_waiting > 0:
        try:
            line = ser.readline().decode('utf-8').strip()
            values = [float(x) for x in line.split(',')]
            if len(values) == 4:
                return values
        except Exception as e:
            print(f"Error: {e}")
    
    # Fallback to simulated data
    time_step += 0.1
    p1 = 50 + 30 * np.sin(time_step)
    p2 = 50 + 30 * np.sin(time_step + np.pi/2)
    p3 = 50 + 30 * np.sin(time_step + np.pi)
    p4 = 50 + 30 * np.sin(time_step + 3*np.pi/2)
    return [p1, p2, p3, p4]

# Main animation loop
print("Starting animation... Close the window to stop.")
try:
    for step in range(5000):
        # Read pressure data
        pressure_values = read_arduino_pressure()
        
        # Update mesh colors
        mesh.cell_data['colors'] = update_mesh_colors(pressure_values)
        
        # Force update the display
        plotter.update()
        
        # Print values
        print(f"Step {step}: P1={pressure_values[0]:.1f} P2={pressure_values[1]:.1f} "
              f"P3={pressure_values[2]:.1f} P4={pressure_values[3]:.1f}")
        
        # Small delay
        time.sleep(0.1)
        
except KeyboardInterrupt:
    print("\nStopped by user")
finally:
    plotter.close()
    if ser:
        ser.close()
