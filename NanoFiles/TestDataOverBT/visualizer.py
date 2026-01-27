import pyvista as pv
import numpy as np
import matplotlib.pyplot as plt
import threading
import time
from esp32_bluetooth import run_bluetooth_thread

# === SHARED DATA ===
latest_pressure = [0.0, 0.0, 0.0, 0.0]  # Shared between BLE thread and visualization
data_lock = threading.Lock()
simulated_time = 0

def parse_sensor_data(raw_data):
    """Parse CSV data from ESP32"""
    try:
        values = raw_data.split(',')
        if len(values) >= 3:
            # Assuming format: timestamp, sensor1, sensor2
            # Modify based on your actual data format
            timestamp = values[0]
            sensor1 = float(values[1])
            sensor2 = float(values[2])
            
            # Map 2 sensors to 4 pressure regions (adjust as needed)
            return [sensor1, sensor2, sensor1 * 0.8, sensor2 * 0.8]
    except Exception as e:
        print(f"Parse error: {e}")
    return None

def bluetooth_data_callback(raw_data):
    """Called when new data arrives from ESP32"""
    global latest_pressure
    
    pressure_values = parse_sensor_data(raw_data)
    if pressure_values:
        with data_lock:
            latest_pressure = pressure_values
        print(f"Received: {raw_data} -> Pressures: {pressure_values}")

def get_current_pressure():
    """Get latest pressure data (thread-safe)"""
    global latest_pressure, simulated_time
    
    with data_lock:
        # If we have real data, use it
        if any(p != 0 for p in latest_pressure):
            return latest_pressure.copy()
    
    # Fallback to simulated data
    simulated_time += 0.1
    p1 = 50 + 30 * np.sin(simulated_time)
    p2 = 50 + 30 * np.sin(simulated_time + np.pi/2)
    p3 = 50 + 30 * np.sin(simulated_time + np.pi)
    p4 = 50 + 30 * np.sin(simulated_time + 3*np.pi/2)
    return [p1, p2, p3, p4]

# === START BLUETOOTH THREAD ===
print("Starting Bluetooth connection in background...")
bt_thread = threading.Thread(
    target=run_bluetooth_thread, 
    args=("ESP32_Sensor", bluetooth_data_callback),
    daemon=True
)
bt_thread.start()

# Give BLE time to connect
time.sleep(3)

# === LOAD 3D MODEL ===
mesh = pv.read('leg.stl')
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

# === CREATE PLOTTER ===
plotter = pv.Plotter()

# Add initial mesh
initial_pressures = [20, 40, 60, 80]
mesh.cell_data['colors'] = update_mesh_colors(initial_pressures)
actor = plotter.add_mesh(mesh, scalars='colors', rgb=True, 
                        show_edges=False, lighting=True)

plotter.show(interactive_update=True, auto_close=False)

# === MAIN ANIMATION LOOP ===
print("Starting visualization... Close the window to stop.")
try:
    for step in range(5000):
        # Get latest pressure data from BLE thread
        pressure_values = get_current_pressure()
        
        # Update mesh colors
        mesh.cell_data['colors'] = update_mesh_colors(pressure_values)
        
        # Force update the display
        plotter.update()
        
        # Print values
        print(f"Step {step}: P1={pressure_values[0]:.1f} P2={pressure_values[1]:.1f} "
              f"P3={pressure_values[2]:.1f} P4={pressure_values[3]:.1f}")
        
        time.sleep(0.1)
        
except KeyboardInterrupt:
    print("\nStopped by user")
finally:
    plotter.close()
    print("Visualization closed")
