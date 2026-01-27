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


def sensor_to_pressure(sensor_value):
    """Convert raw sensor bits to pressure value (0-2 range)"""
    if sensor_value == 0:
        return 0.0
    pressure = cal_slope * sensor_value + cal_intercept
    return np.clip(pressure, 0, 2)


# === ARDUINO CONNECTION ===
def find_arduino_port(baudrate=9600, timeout=0.01):
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

    print("No Arduino found, using simulated data")
    return None


ser = find_arduino_port()

if ser is None:
    print("Warning: Arduino not found, using simulated data")


# === LOAD 3D MODEL ===
mesh = pv.read('leg.stl')
cell_centers = mesh.cell_centers().points


# Single pressure patch center
patch_center = [79.22101593, 12.75070763, 155.10850525]
patch_radius = 15.0


# Identify cells in the pressure region
distances = np.linalg.norm(cell_centers - patch_center, axis=1)
region_mask = distances < patch_radius


# Color mapping
max_pressure = 2.0


def get_color_from_pressure(pressure):
    """Map pressure (0-2) to color using jet colormap"""
    intensity = np.clip(pressure / max_pressure, 0, 1)
    colormap = plt.get_cmap('jet')
    rgba = colormap(intensity)
    return rgba[:3]


def update_mesh_colors(pressure_value):
    """Update mesh colors: pressure region gets colored, rest stays gray"""
    colors = np.zeros((mesh.n_cells, 3))
    colors[:] = [0.8, 0.8, 0.8]  # Gray background

    # Color the pressure region
    color = get_color_from_pressure(pressure_value)
    colors[region_mask] = color

    return colors


# === CREATE PLOTTER ===
plotter = pv.Plotter()


# Add initial mesh
initial_pressure = 1.0
mesh.cell_data['colors'] = update_mesh_colors(initial_pressure)
actor = plotter.add_mesh(mesh, scalars='colors', rgb=True, 
                        show_edges=False, lighting=True)


# Show with interactive update
plotter.show(interactive_update=True, auto_close=False)


# === READ FROM ARDUINO WITH AVERAGING ===
sim_time = 0


def collect_readings_for_duration(duration=1.0):
    """Collect all readings over the specified duration and return average"""
    global sim_time

    readings = []
    start_time = time.time()

    while (time.time() - start_time) < duration:
        if ser and ser.in_waiting > 0:
            try:
                line = ser.readline().decode('utf-8').strip()
                if line:
                    raw_value = float(line)
                    pressure = sensor_to_pressure(raw_value)
                    readings.append(pressure)
            except Exception as e:
                pass
        else:
            # Simulated data
            sim_time += 0.01
            pressure = 1.0 + 0.8 * np.sin(sim_time)
            readings.append(pressure)
            time.sleep(0.01)  # Small delay for simulation

    # Return average, or fallback value if no readings
    if readings:
        return np.mean(readings), len(readings)
    else:
        return 1.0, 0


# === MAIN ANIMATION LOOP ===
print("Starting animation... Updating every 1 second with averaged readings.")
print("Close the window to stop.")
try:
    for step in range(5000):
        # Collect readings over 1 second and average
        avg_pressure, num_readings = collect_readings_for_duration(duration=5.0)

        # Update mesh colors
        mesh.cell_data['colors'] = update_mesh_colors(avg_pressure)

        # Force update the display
        plotter.update()

        # Print value
        print(f"Step {step}: Pressure = {avg_pressure:.2f} (avg of {num_readings} readings)")

except KeyboardInterrupt:
    print("\nStopped by user")
finally:
    plotter.close()
    if ser:
        ser.close()
