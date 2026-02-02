import pyvista as pv
import numpy as np
import matplotlib.pyplot as plt
import threading
import time
from esp32_bluetooth import run_bluetooth_thread, send_command_sync


# === SHARED DATA ===
latest_pressure = [0.0, 0.0, 0.0, 0.0]  # Shared between BLE thread and visualization
data_lock = threading.Lock()
simulated_time = 0
ble_characteristic = None  # Will hold BLE write handle


def parse_sensor_data(raw_data):
    """Parse CSV data from ESP32: timestamp,p1,p2,p3,p4"""
    try:
        # Strip whitespace and decode if bytes
        if isinstance(raw_data, bytes):
            raw_data = raw_data.decode('utf-8').strip()
        else:
            raw_data = raw_data.strip()
            
        values = raw_data.split(',')
        if len(values) >= 5:  # timestamp + 4 sensors
            timestamp = int(values[0])
            sensor1 = float(values[1])
            sensor2 = float(values[2])
            sensor3 = float(values[3])
            sensor4 = float(values[4])
            
            return [sensor1, sensor2, sensor3, sensor4]
    except Exception as e:
        print(f"Parse error: {e} | Raw: {raw_data}")
    return None


def bluetooth_data_callback(raw_data):
    """Called when new data arrives from ESP32"""
    global latest_pressure
    
    pressure_values = parse_sensor_data(raw_data)
    if pressure_values:
        with data_lock:
            latest_pressure = pressure_values
        print(f"BLE Update -> P1={pressure_values[0]:.0f} P2={pressure_values[1]:.0f} "
              f"P3={pressure_values[2]:.0f} P4={pressure_values[3]:.0f}")


def get_current_pressure():
    """Get latest pressure data (thread-safe)"""
    global latest_pressure, simulated_time
    
    with data_lock:
        # If we have real data, use it
        if any(p != 0 for p in latest_pressure):
            return latest_pressure.copy()
    
    # Fallback to simulated data if no BLE connection
    simulated_time += 0.1
    p1 = 50 * np.sin(simulated_time)
    p2 = 50 * np.sin(simulated_time + np.pi/2)
    p3 = 50 * np.sin(simulated_time + np.pi)
    p4 = 50 * np.sin(simulated_time + 3*np.pi/2)
    return [p1, p2, p3, p4]


# Replace the old send_tare_command() with:
def send_tare_command():
    """Send tare command to ESP32 via BLE"""
    try:
        success = send_command_sync("TARE")
        if success:
            print("✓ Tare command sent to ESP32")
        else:
            print("✗ BLE not connected, cannot send tare command")
    except Exception as e:
        print(f"✗ Failed to send tare command: {e}")


# === START BLUETOOTH THREAD ===
print("Starting Bluetooth connection to ESP32_LoadCells...")
bt_thread = threading.Thread(
    target=run_bluetooth_thread, 
    args=("ESP32_LoadCells", bluetooth_data_callback),
    daemon=True
)
bt_thread.start()


# Give BLE time to connect and tare sensors
print("Waiting for ESP32 to initialize and tare sensors...")
time.sleep(15)


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


patch_radius = 25.0


# Assign regions
region_ids = np.full(mesh.n_cells, -1)
for region_idx, center in enumerate(patch_centers):
    distances = np.linalg.norm(cell_centers - center, axis=1)
    within_radius = distances < patch_radius
    region_ids[within_radius] = region_idx


mesh['region'] = region_ids


# Pressure range: -100 to +100
min_pressure = -100.0
max_pressure = 100.0


def get_color_from_pressure(pressure):
    """Map pressure (-100 to +100) to color using jet colormap"""
    normalized = (pressure - min_pressure) / (max_pressure - min_pressure)
    normalized = np.clip(normalized, 0, 1)
    
    colormap = plt.get_cmap('jet')
    rgba = colormap(normalized)
    return rgba[:3]


def update_mesh_colors(pressure_values):
    colors = np.zeros((mesh.n_cells, 3))
    colors[:] = [0.8, 0.8, 0.8]
    
    for i in range(4):
        mask = mesh['region'] == i
        if np.any(mask):
            pressure = np.clip(pressure_values[i], min_pressure, max_pressure)
            color = get_color_from_pressure(pressure)
            colors[mask] = color
    
    return colors


# === CREATE PLOTTER WITH BUTTON ===
plotter = pv.Plotter()


# Add tare button
def tare_callback():
    """Callback when tare button is pressed"""
    print("\n[TARE] Button pressed - sending command to ESP32...")
    send_tare_command()


plotter.add_text("Press 'T' key or click button to tare sensors", 
                 position='upper_left', font_size=10, color='white')


# Add keyboard shortcut for tare (T key)
plotter.add_key_event('t', tare_callback)
plotter.add_key_event('T', tare_callback)


# Add initial mesh
initial_pressures = [0, 0, 0, 0]
mesh.cell_data['colors'] = update_mesh_colors(initial_pressures)
actor = plotter.add_mesh(mesh, scalars='colors', rgb=True, 
                        show_edges=False, lighting=True)


plotter.show(interactive_update=True, auto_close=False)


# === MAIN ANIMATION LOOP ===
print("Starting visualization... Close the window to stop.")
print("Pressure range: -100 (blue) to 0 (green) to +100 (red)")
print("Press 'T' key to tare/zero sensors")
try:
    for step in range(5000):
        # Get latest pressure data from BLE thread
        pressure_values = get_current_pressure()
        
        # Update mesh colors
        mesh.cell_data['colors'] = update_mesh_colors(pressure_values)
        
        # Force update the display
        plotter.update()
        
        # Print values every 10 steps
        if step % 10 == 0:
            print(f"Step {step}: P1={pressure_values[0]:.0f} P2={pressure_values[1]:.0f} "
                  f"P3={pressure_values[2]:.0f} P4={pressure_values[3]:.0f}")
        
        time.sleep(0.1)
        
except KeyboardInterrupt:
    print("\nStopped by user")
finally:
    plotter.close()
    print("Visualization closed")
