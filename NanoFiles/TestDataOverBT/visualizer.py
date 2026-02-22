import pyvista as pv
import numpy as np
import matplotlib.pyplot as plt
import threading
import time
import tkinter as tk
from tkinter import ttk
import json
import os
from esp32_bluetooth import run_bluetooth_thread, send_command_sync


# === CONFIGURATION ===
CONFIG_FILE = "ideal_pressures.json"
ideal_pressure_values = [0.0, 0.0, 0.0, 0.0]
threshold_range = 20  # ±20 from ideal


# === SHARED DATA ===
latest_pressure = [0.0, 0.0, 0.0, 0.0]
manual_pressure_values = [0.0, 0.0, 0.0, 0.0]
captured_pressure = [0.0, 0.0, 0.0, 0.0]  # NEW: Snapshot when READ button clicked
use_captured = False  # NEW: Flag to use captured values
data_lock = threading.Lock()
using_real_data = False


# === BOA CONFIGURATION ===
boa_info = {
    0: {'name': 'BOA 1 (Front)', 'position': [79.22101593, 12.75070763, 155.10850525]},
    1: {'name': 'BOA 2 (Side)', 'position': [28.12449265, 48.21684265, 159.52259827]},
    2: {'name': 'BOA 3 (Back)', 'position': [76.4567337, 108.86454773, 137.45446777]},
    3: {'name': 'BOA 4 (Top)', 'position': [118.10018921, 54.5916481, 130.84025574]},
}


def load_ideal_pressures():
    """Load stored ideal pressure values"""
    global ideal_pressure_values
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                data = json.load(f)
                ideal_pressure_values = data.get('ideal_pressures', [0.0, 0.0, 0.0, 0.0])
                print(f"✓ Loaded ideal pressures: {ideal_pressure_values}")
        else:
            print("No saved ideal pressures found, using defaults (0,0,0,0)")
    except Exception as e:
        print(f"Error loading ideal pressures: {e}")


def save_ideal_pressures(values):
    """Save ideal pressure values to file"""
    global ideal_pressure_values
    try:
        ideal_pressure_values = values.copy()
        with open(CONFIG_FILE, 'w') as f:
            json.dump({'ideal_pressures': values}, f, indent=2)
        print(f"✓ Saved ideal pressures: {values}")
        return True
    except Exception as e:
        print(f"Error saving ideal pressures: {e}")
        return False


def get_boa_recommendation(pressure_value, sensor_index):
    """Determine if BOA needs adjustment relative to ideal pressure"""
    ideal = ideal_pressure_values[sensor_index]
    deviation = pressure_value - ideal
    
    if deviation > threshold_range:
        return "↻ LOOSEN", (1.0, 0.2, 0.2)  # Red
    elif deviation < -threshold_range:
        return "↺ TIGHTEN", (0.2, 0.2, 1.0)  # Blue
    else:
        return "✓ OK", (0.2, 1.0, 0.2)  # Green


def parse_sensor_data(raw_data):
    """Parse CSV data from ESP32: timestamp,p1,p2,p3,p4"""
    try:
        if isinstance(raw_data, bytes):
            raw_data = raw_data.decode('utf-8').strip()
        else:
            raw_data = raw_data.strip()
            
        values = raw_data.split(',')
        if len(values) >= 5:
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
    global latest_pressure, using_real_data
    pressure_values = parse_sensor_data(raw_data)
    if pressure_values:
        with data_lock:
            latest_pressure = pressure_values
            using_real_data = True
        print(f"BLE -> P1={pressure_values[0]:.0f} P2={pressure_values[1]:.0f} "
              f"P3={pressure_values[2]:.0f} P4={pressure_values[3]:.0f}")


def get_current_pressure():
    """Get latest pressure data (thread-safe)"""
    global latest_pressure, using_real_data, manual_pressure_values
    
    with data_lock:
        if using_real_data:
            return latest_pressure.copy()
    
    return manual_pressure_values.copy()


def get_display_pressure():
    """Get pressure values for display - either captured snapshot or live"""
    global captured_pressure, use_captured
    
    if use_captured:
        return captured_pressure.copy()
    else:
        return get_current_pressure()


def send_tare_command():
    """Send tare command to ESP32 via BLE"""
    try:
        success = send_command_sync("TARE")
        if success:
            print("✓ Tare command sent to ESP32")
            return True
        else:
            print("✗ BLE not connected")
            return False
    except Exception as e:
        print(f"✗ Tare failed: {e}")
        return False


# === SIMULATION CONTROL PANEL ===
def create_simulation_panel():
    """Create manual simulation control panel"""
    sim_root = tk.Tk()
    sim_root.title("Simulation Control")
    sim_root.geometry("400x550")
    sim_root.configure(bg='#1a1a1a')
    
    title = tk.Label(sim_root, text="📊 Manual Pressure Control", 
                     font=('Arial', 16, 'bold'),
                     bg='#1a1a1a', fg='orange')
    title.pack(pady=15)
    
    info = tk.Label(sim_root, text="(Used when no BLE connection)", 
                   font=('Arial', 9, 'italic'),
                   bg='#1a1a1a', fg='gray')
    info.pack()
    
    sliders = []
    
    for i in range(4):
        frame = tk.LabelFrame(sim_root, text=f"  {boa_info[i]['name']}  ",
                             font=('Arial', 10, 'bold'),
                             bg='#2a2a2a', fg='white',
                             padx=15, pady=10,
                             relief='ridge', bd=2)
        frame.pack(fill='x', padx=15, pady=8)
        
        value_label = tk.Label(frame, text="0.0", 
                              font=('Courier', 14, 'bold'),
                              bg='#2a2a2a', fg='white')
        value_label.pack()
        
        def make_slider_callback(index, label):
            def callback(val):
                manual_pressure_values[index] = float(val)
                label.config(text=f"{float(val):+6.1f}")
            return callback
        
        slider = tk.Scale(frame, from_=-100, to=100, 
                         orient='horizontal',
                         bg='#2a2a2a', fg='white',
                         troughcolor='#404040',
                         highlightthickness=0,
                         length=300,
                         resolution=0.1,
                         command=make_slider_callback(i, value_label))
        slider.set(0)
        slider.pack(pady=5)
        
        sliders.append((slider, value_label))
    
    def reset_all():
        for slider, label in sliders:
            slider.set(0)
    
    reset_btn = tk.Button(sim_root, text="⟲ Reset All to Zero", 
                         command=reset_all,
                         bg='#555', fg='white',
                         font=('Arial', 11, 'bold'),
                         height=2,
                         cursor='hand2')
    reset_btn.pack(pady=15, padx=20, fill='x')
    
    sim_root.mainloop()


# === TKINTER CONTROL PANEL ===
def create_control_panel():
    """Create Tkinter control panel with buttons"""
    global use_captured, captured_pressure
    
    root = tk.Tk()
    root.title("BOA Control Panel")
    root.geometry("420x850")
    root.configure(bg='#2b2b2b')
    
    title = tk.Label(root, text="🦿 Prosthetic Socket Monitor", 
                     font=('Arial', 18, 'bold'),
                     bg='#2b2b2b', fg='white')
    title.pack(pady=15)
    
    conn_frame = tk.Frame(root, bg='#2b2b2b')
    conn_frame.pack()
    
    conn_indicator = tk.Label(conn_frame, text="●", 
                             font=('Arial', 14),
                             bg='#2b2b2b', fg='yellow')
    conn_indicator.pack(side='left')
    
    conn_label = tk.Label(conn_frame, text="Manual Control", 
                         font=('Arial', 10),
                         bg='#2b2b2b', fg='yellow')
    conn_label.pack(side='left', padx=5)
    
    boa_labels = []
    
    for i in range(4):
        frame = tk.LabelFrame(root, text=f"  {boa_info[i]['name']}  ", 
                             font=('Arial', 11, 'bold'),
                             bg='#3c3c3c', fg='white',
                             padx=15, pady=10,
                             relief='ridge', bd=3)
        frame.pack(fill='x', padx=15, pady=8)
        
        pressure_label = tk.Label(frame, text="Pressure: ---", 
                                 font=('Courier', 13, 'bold'),
                                 bg='#3c3c3c', fg='white')
        pressure_label.pack()
        
        action_label = tk.Label(frame, text="Click READ to test", 
                               font=('Arial', 16, 'bold'),
                               bg='#3c3c3c', fg='gray')
        action_label.pack(pady=5)
        
        boa_labels.append((pressure_label, action_label, frame))
    
    separator = tk.Frame(root, height=2, bg='gray', relief='sunken')
    separator.pack(fill='x', padx=15, pady=15)
    
    status_label = tk.Label(root, text="Ready - Click READ to capture values", 
                           font=('Arial', 11, 'italic'),
                           bg='#2b2b2b', fg='#33ff33')
    status_label.pack(pady=5)
    
    # READ/TEST button
    def read_test_pressed():
        global use_captured, captured_pressure
        
        read_btn.config(state='disabled', text="📸 Reading...")
        status_label.config(text="Capturing pressure snapshot...", fg='yellow')
        
        def do_read():
            global use_captured, captured_pressure
            current = get_current_pressure()
            captured_pressure = current.copy()
            use_captured = True
            root.after(0, lambda: update_after_read(current))
        
        def update_after_read(values):
            status_label.config(
                text=f"✓ Captured: [{values[0]:.0f}, {values[1]:.0f}, {values[2]:.0f}, {values[3]:.0f}]", 
                fg='cyan'
            )
            root.after(1500, lambda: read_btn.config(state='normal', text="📸 READ / TEST"))
        
        threading.Thread(target=do_read, daemon=True).start()
    
    read_btn = tk.Button(root, text="📸 READ / TEST", 
                        command=read_test_pressed,
                        bg='#3388ff', fg='white',
                        font=('Arial', 13, 'bold'),
                        height=2, relief='raised', bd=4,
                        activebackground='#5599ff',
                        cursor='hand2')
    read_btn.pack(pady=5, padx=20, fill='x')
    
    # SET BASELINE button
    def set_ideal_pressed():
        current_values = get_display_pressure()
        set_btn.config(state='disabled', text="⊙ Setting...")
        status_label.config(text="Storing as baseline...", fg='yellow')
        
        def do_set():
            success = save_ideal_pressures(current_values)
            root.after(0, lambda: update_after_set(success, current_values))
        
        def update_after_set(success, values):
            if success:
                status_label.config(
                    text=f"✓ Baseline: [{values[0]:.0f}, {values[1]:.0f}, {values[2]:.0f}, {values[3]:.0f}]", 
                    fg='#33ff33'
                )
            else:
                status_label.config(text="✗ Failed to save", fg='red')
            root.after(3000, lambda: status_label.config(text="Ready", fg='#33ff33'))
            root.after(2000, lambda: set_btn.config(state='normal', text="⊙ SET BASELINE"))
        
        threading.Thread(target=do_set, daemon=True).start()
    
    set_btn = tk.Button(root, text="⊙ SET BASELINE", 
                       command=set_ideal_pressed,
                       bg='#33aa33', fg='white',
                       font=('Arial', 12, 'bold'),
                       height=2, relief='raised', bd=4,
                       activebackground='#44bb44',
                       cursor='hand2')
    set_btn.pack(pady=5, padx=20, fill='x')
    
    # Tare button
    def tare_pressed():
        tare_btn.config(state='disabled', text="⟳ Taring...")
        status_label.config(text="Sending tare command...", fg='yellow')
        
        def do_tare():
            success = send_tare_command()
            root.after(0, lambda: update_after_tare(success))
        
        def update_after_tare(success):
            if success:
                status_label.config(text="✓ All sensors tared!", fg='#33ff33')
            else:
                status_label.config(text="✗ Tare failed - Check BLE", fg='red')
            root.after(2000, lambda: status_label.config(text="Ready", fg='#33ff33'))
            root.after(2000, lambda: tare_btn.config(state='normal', text="⟳ TARE ALL SENSORS"))
        
        threading.Thread(target=do_tare, daemon=True).start()
    
    tare_btn = tk.Button(root, text="⟳ TARE ALL SENSORS", 
                        command=tare_pressed,
                        bg='#ff9933', fg='black',
                        font=('Arial', 14, 'bold'),
                        height=2, relief='raised', bd=4,
                        activebackground='#ffaa55',
                        cursor='hand2')
    tare_btn.pack(pady=5, padx=20, fill='x')
    
    instructions = tk.Label(root, 
                           text="Workflow: READ → Analyze → SET BASELINE\n3D View: T=Tare | Q=Quit", 
                           font=('Arial', 9),
                           bg='#2b2b2b', fg='gray',
                           justify='center')
    instructions.pack(pady=10)
    
    update_count = [0]
    
    def update_panel():
        try:
            pressure_values = get_display_pressure()  # Use captured or live
            update_count[0] += 1
            
            if using_real_data:
                conn_indicator.config(fg='#33ff33')
                conn_label.config(text="Bluetooth Connected", fg='#33ff33')
            else:
                conn_indicator.config(fg='orange')
                conn_label.config(text="Manual Control", fg='orange')
            
            for i, (p_label, a_label, frame) in enumerate(boa_labels):
                p_label.config(text=f"Pressure: {pressure_values[i]:+6.1f}")
                
                if use_captured:
                    action, color_rgb = get_boa_recommendation(pressure_values[i], i)
                    
                    color_hex = '#{:02x}{:02x}{:02x}'.format(
                        int(color_rgb[0]*255), 
                        int(color_rgb[1]*255), 
                        int(color_rgb[2]*255)
                    )
                    
                    a_label.config(text=action, fg=color_hex)
                    
                    ideal = ideal_pressure_values[i]
                    deviation = pressure_values[i] - ideal
                    
                    if deviation > threshold_range:
                        frame.config(bg='#4d2626')
                        p_label.config(bg='#4d2626')
                        a_label.config(bg='#4d2626')
                    elif deviation < -threshold_range:
                        frame.config(bg='#26264d')
                        p_label.config(bg='#26264d')
                        a_label.config(bg='#26264d')
                    else:
                        frame.config(bg='#264d26')
                        p_label.config(bg='#264d26')
                        a_label.config(bg='#264d26')
                else:
                    a_label.config(text="Click READ to test", fg='gray')
                    frame.config(bg='#3c3c3c')
                    p_label.config(bg='#3c3c3c')
                    a_label.config(bg='#3c3c3c')
            
            root.after(100, update_panel)
        except Exception as e:
            print(f"[Tkinter] Error: {e}")
            root.after(100, update_panel)
    
    update_panel()
    root.mainloop()


# === LOAD SAVED CONFIGURATION ===
print("="*50)
print("Loading configuration...")
load_ideal_pressures()
print("="*50)


# === START BLUETOOTH ===
print("Starting Bluetooth connection...")
bt_thread = threading.Thread(
    target=run_bluetooth_thread, 
    args=("ESP32_LoadCells", bluetooth_data_callback),
    daemon=True
)
bt_thread.start()
print("Waiting for ESP32...")
time.sleep(15)


# === START SIMULATION CONTROL PANEL ===
print("Launching simulation control...")
sim_thread = threading.Thread(target=create_simulation_panel, daemon=True)
sim_thread.start()
time.sleep(0.5)


# === START TKINTER CONTROL PANEL ===
print("Launching control panel...")
control_thread = threading.Thread(target=create_control_panel, daemon=True)
control_thread.start()
time.sleep(1)


# === LOAD 3D MODEL ===
print("Loading 3D model...")
mesh = pv.read('leg.stl')
cell_centers = mesh.cell_centers().points


patch_centers = [info['position'] for info in boa_info.values()]
patch_radius = 25.0
region_ids = np.full(mesh.n_cells, -1)
for region_idx, center in enumerate(patch_centers):
    distances = np.linalg.norm(cell_centers - center, axis=1)
    within_radius = distances < patch_radius
    region_ids[within_radius] = region_idx


mesh['region'] = region_ids
min_pressure = -100.0
max_pressure = 100.0


def update_mesh_colors(pressure_values):
    colors = np.zeros((mesh.n_cells, 3))
    colors[:] = [0.8, 0.8, 0.8]
    
    for i in range(4):
        mask = mesh['region'] == i
        if np.any(mask):
            pressure = pressure_values[i]
            ideal = ideal_pressure_values[i]
            
            # Map relative to ideal: ideal±50 range mapped to 0-1
            # ideal-50 = blue (0), ideal = green (0.5), ideal+50 = red (1)
            deviation = pressure - ideal
            normalized = (deviation + 50) / 100  # Maps -50 to +50 → 0 to 1
            normalized = np.clip(normalized, 0, 1)
            
            colormap = plt.get_cmap('jet')
            rgba = colormap(normalized)
            color = rgba[:3]
            colors[mask] = color
    
    return colors


print("Creating visualization...")
plotter = pv.Plotter()


initial_pressures = [0, 0, 0, 0]
mesh.cell_data['colors'] = update_mesh_colors(initial_pressures)
actor = plotter.add_mesh(mesh, scalars='colors', rgb=True, 
                        show_edges=False, lighting=True)


for i, info in boa_info.items():
    sphere = pv.Sphere(radius=5, center=info['position'])
    plotter.add_mesh(sphere, color='yellow', opacity=0.9)
    
    plotter.add_point_labels(
        [info['position']], 
        [info['name']], 
        font_size=12,
        point_size=0,
        text_color='white',
        bold=True,
        shape_color='black',
        shape_opacity=0.7
    )


plotter.add_text(
    "3D Pressure Heat Map", 
    position='upper_edge',
    font_size=14,
    color='white',
    font='arial',
    shadow=True
)


plotter.add_text(
    f"Scale (relative to baseline):\n"
    f"Blue = -{threshold_range}\n"
    f"Green = Baseline\n"
    f"Red = +{threshold_range}",
    position=(0.02, 0.15),
    font_size=10,
    color='yellow',
    font='arial',
    shadow=True
)


def tare_callback():
    print("\n[TARE] 'T' key pressed!")
    send_tare_command()


plotter.add_key_event('t', tare_callback)
plotter.add_key_event('T', tare_callback)


plotter.show(interactive_update=True, auto_close=False)


print("\n" + "="*50)
print("Visualization running!")
print("="*50 + "\n")


try:
    while True:
        pressure_values = get_display_pressure()  # Use captured or live
        mesh.cell_data['colors'] = update_mesh_colors(pressure_values)
        plotter.update()
        time.sleep(0.1)
        
        # Check if plotter window is still open
        if not plotter.ren_win:
            break
            
except KeyboardInterrupt:
    print("\nStopped by user")
except Exception as e:
    print(f"\nVisualization ended: {e}")
finally:
    plotter.close()
    print("Closed")
