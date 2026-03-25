from hyperframe import frame
import pyvista as pv
import numpy as np
import matplotlib.pyplot as plt
import threading
import time
import tkinter as tk
from scipy.spatial import Delaunay
from sensor_sdk import SocketSensor
from utils import resource_path
from regions import boa_regions, build_regions

# === CONFIGURATION ===
sensor = SocketSensor(device_name="ESP32_LoadCells", threshold=4, sample_count=20)


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
        frame = tk.LabelFrame(sim_root, text=f"  {boa_regions[i]['name']}  ",
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
                sensor.set_manual(index, float(val))
                label.config(text=f"{float(val):+6.1f}")
            return callback

        slider = tk.Scale(frame, from_=-25, to=15,
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
        for i, (slider, label) in enumerate(sliders):
            slider.set(0)
            sensor.set_manual(i, 0.0)

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
        frame = tk.LabelFrame(root, text=f"  {boa_regions[i]['name']}  ",
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
        read_btn.config(state='disabled', text="📸 Reading...")
        status_label.config(text="Collecting samples: 0 / 75", fg='yellow')

        def progress(current, total):
            root.after(0, lambda: status_label.config(
                text=f"Collecting samples: {current} / {total}", fg='yellow'
            ))

        def do_read():
            values = sensor.capture(progress_callback=progress)
            root.after(0, lambda: update_after_read(values))

        def update_after_read(values):
            status_label.config(
                text=f"✓ Captured: [{values[0]:.1f}, {values[1]:.1f}, {values[2]:.1f}, {values[3]:.1f}]",
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
        set_btn.config(state='disabled', text="⊙ Setting...")
        status_label.config(text="Collecting samples: 0 / 75", fg='yellow')

        def progress(current, total):
            root.after(0, lambda: status_label.config(
                text=f"Collecting samples: {current} / {total}", fg='yellow'
            ))

        def do_set():
            success = sensor.set_baseline(progress_callback=progress)
            values = sensor.get_baseline()
            root.after(0, lambda: update_after_set(success, values))

        def update_after_set(success, values):
            if success:
                status_label.config(
                    text=f"✓ Baseline: [{values[0]:.1f}, {values[1]:.1f}, {values[2]:.1f}, {values[3]:.1f}]",
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
            success = sensor.tare()
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

    def update_panel():
        try:
            # Live pressures for display
            pressurevalues = sensor.get_live()  # Or keep get_display() if renamed
            
            # Analysis only if captured
            if sensor.has_capture:
                for i, (plabel, alabel, frame) in enumerate(boa_labels):
                    plabel.config(text=f"Pressure: {pressurevalues[i]:.1f}")
                    
                    action, color_rgb = sensor.get_recommendation(i)
                    color_hex = "#{:02x}{:02x}{:02x}".format(
                        int(color_rgb[0]*255), int(color_rgb[1]*255), int(color_rgb[2]*255)
                    )
                    alabel.config(text=action, fg=color_hex)
                    
                    dev = sensor.get_deviation(i)
                    if abs(dev) > sensor.threshold:
                        frame.config(bg="#4d2626" if dev > 0 else "#26264d")
                    else:
                        frame.config(bg="#264d26")
            else:
                for i, (plabel, alabel, frame) in enumerate(boa_labels):  # ← i defined here now
                    plabel.config(text=f"Pressure: {pressurevalues[i]:.1f}")
                    alabel.config(text="Click READ to analyze", fg="gray")
                    frame.config(bg="#3c3c3c")
                    plabel.config(bg="#3c3c3c")
                    alabel.config(bg="#3c3c3c")
            
            root.after(100, update_panel)
        except Exception as e:
            print(f"Tkinter Error: {e}")
            root.after(100, update_panel)


    update_panel()
    root.mainloop()


# === REGION ASSIGNMENT (Convex Hull) ===
def build_regions(cell_centers):
    """Assign each mesh cell to a BOA region using convex hull zones"""
    region_ids = np.full(len(cell_centers), -1)

    for region_idx, info in boa_regions.items():
        for zone_points in info['zones']:
            try:
                delaunay = Delaunay(zone_points)
                inside = delaunay.find_simplex(cell_centers) >= 0
                region_ids[inside] = region_idx
            except Exception as e:
                print(f"⚠ Zone error for {info['name']}: {e}")

    assigned = np.sum(region_ids >= 0)
    print(f"✓ Region assignment: {assigned}/{len(cell_centers)} cells assigned")
    for i, info in boa_regions.items():
        count = np.sum(region_ids == i)
        print(f"   {info['name']}: {count} cells")

    return region_ids


# === HEATMAP COLORING ===
def update_mesh_colors(pressure_values):
    colors = np.zeros((mesh.n_cells, 3))
    colors[:] = [0.8, 0.8, 0.8]

    baseline = sensor.get_baseline()

    for i in range(4):
        mask = mesh['region'] == i
        if np.any(mask):
            deviation = pressure_values[i] - baseline[i]

            normalized = (-deviation + 30) / 60
            normalized = np.clip(normalized, 0, 1)

            colormap = plt.get_cmap('jet')
            rgba = colormap(normalized)
            colors[mask] = rgba[:3]

    return colors


# === SPLASH / CONNECTION WINDOW ===
def create_splash_window():
    """
    Blocking splash window shown while waiting for BLE.
    Returns True if user chose simulation mode, False if BLE connected.
    """
    splash = tk.Tk()
    splash.title("Prosthetic Socket Monitor")
    splash.geometry("420x320")
    splash.configure(bg='#1a1a1a')
    splash.resizable(False, False)

    # Center the window
    splash.eval('tk::PlaceWindow . center')

    result = [None]  # 'sim' or 'ble'

    title = tk.Label(splash, text="🦿 Prosthetic Socket Monitor",
                     font=('Arial', 16, 'bold'),
                     bg='#1a1a1a', fg='white')
    title.pack(pady=20)

    status_label = tk.Label(splash,
                            text="Searching for ESP32_LoadCells...",
                            font=('Arial', 11),
                            bg='#1a1a1a', fg='yellow')
    status_label.pack(pady=5)

    # Animated dots indicator
    dot_label = tk.Label(splash, text="⬤ ⬤ ⬤",
                         font=('Arial', 18),
                         bg='#1a1a1a', fg='#3388ff')
    dot_label.pack(pady=10)

    conn_frame = tk.Frame(splash, bg='#1a1a1a')
    conn_frame.pack(pady=5)

    conn_indicator = tk.Label(conn_frame, text="●",
                              font=('Arial', 14),
                              bg='#1a1a1a', fg='yellow')
    conn_indicator.pack(side='left')

    conn_text = tk.Label(conn_frame, text="Waiting for Bluetooth...",
                         font=('Arial', 10),
                         bg='#1a1a1a', fg='yellow')
    conn_text.pack(side='left', padx=5)

    separator = tk.Frame(splash, height=1, bg='gray')
    separator.pack(fill='x', padx=30, pady=15)

    skip_label = tk.Label(splash,
                          text="No device available?",
                          font=('Arial', 10, 'italic'),
                          bg='#1a1a1a', fg='gray')
    skip_label.pack()

    def use_simulation():
        result[0] = 'sim'
        status_label.config(text="Starting in simulation mode...", fg='orange')
        conn_indicator.config(fg='orange')
        conn_text.config(text="Simulation Mode", fg='orange')
        sim_btn.config(state='disabled')
        splash.after(800, splash.destroy)

    sim_btn = tk.Button(splash, text="▶  Use Simulated Data",
                        command=use_simulation,
                        bg='#ff9933', fg='black',
                        font=('Arial', 12, 'bold'),
                        height=2, relief='raised', bd=3,
                        activebackground='#ffaa55',
                        cursor='hand2')
    sim_btn.pack(pady=10, padx=40, fill='x')

    # Animate the dots
    dot_states = ['⬤ ○ ○', '○ ⬤ ○', '○ ○ ⬤', '⬤ ⬤ ○', '○ ⬤ ⬤', '⬤ ⬤ ⬤']
    dot_idx = [0]

    def animate_dots():
        if result[0] is None:
            dot_label.config(text=dot_states[dot_idx[0] % len(dot_states)])
            dot_idx[0] += 1
            splash.after(400, animate_dots)

    animate_dots()

    # Poll for BLE connection in background
    def poll_connection():
        if result[0] is not None:
            return
        if sensor.is_connected:
            result[0] = 'ble'
            status_label.config(text="✓ Bluetooth Connected!", fg='#33ff33')
            conn_indicator.config(fg='#33ff33')
            conn_text.config(text="ESP32 Connected", fg='#33ff33')
            dot_label.config(text="⬤ ⬤ ⬤", fg='#33ff33')
            sim_btn.config(state='disabled')
            splash.after(1000, splash.destroy)
        else:
            splash.after(500, poll_connection)

    poll_connection()
    splash.mainloop()

    return result[0] == 'sim'



# === STARTUP ===
print("="*50)
print("Loading configuration...")
sensor.load_baseline()
print("="*50)

# Start BLE connection attempt in background
print("Starting Bluetooth connection...")
sensor.connect()

# Show splash window — blocks until connected or user picks simulation
print("Showing splash window...")
simulation_mode = create_splash_window()

if simulation_mode:
    print("▶ Running in SIMULATION mode")
else:
    print("✓ Running with BLUETOOTH connection")

# Launch simulation panel ONLY if in simulation mode
if simulation_mode:
    print("Launching simulation control...")
    sim_thread = threading.Thread(target=create_simulation_panel, daemon=True)
    sim_thread.start()
    sensor.start_manual_stream()
    time.sleep(0.5)

# Always launch main control panel
print("Launching control panel...")
control_thread = threading.Thread(target=create_control_panel, daemon=True)
control_thread.start()
time.sleep(1)



# === LOAD 3D MODEL ===
print("Loading 3D model...")
mesh = pv.read(resource_path('leg.stl'))

print("Refining mesh...")
mesh = mesh.clean()                         # Fix any bad geometry first
mesh = mesh.subdivide(2, subfilter='loop')  # 16x more cells, smooth curves
print(f"✓ Mesh refined: {mesh.n_cells} cells total")

# Recalculate cell centers AFTER subdivision
cell_centers = mesh.cell_centers().points

# Full mesh bounds
print(f"FULL MESH:")
print(f"  X: {cell_centers[:,0].min():.1f} → {cell_centers[:,0].max():.1f}")
print(f"  Y: {cell_centers[:,1].min():.1f} → {cell_centers[:,1].max():.1f}")
print(f"  Z: {cell_centers[:,2].min():.1f} → {cell_centers[:,2].max():.1f}")

# Count how many cells fall within those bounds
mask = (
    (cell_centers[:,0] >= 49.0) & (cell_centers[:,0] <= 98.0) &
    (cell_centers[:,1] >= -105.0) & (cell_centers[:,1] <= 13.0) &
    (cell_centers[:,2] >= 198.0) & (cell_centers[:,2] <= 223.0)
)
print(f"\nCells within BOA 1 bounding box: {mask.sum()}")


print("Building regions...")
region_ids = build_regions(cell_centers)
mesh['region'] = region_ids


# === 3D PLOTTER SETUP ===
print("Creating visualization...")
plotter = pv.Plotter()

mesh.cell_data['colors'] = update_mesh_colors([0, 0, 0, 0])
actor = plotter.add_mesh(mesh, scalars='colors', rgb=True,
                        show_edges=False, lighting=True)

for i, info in boa_regions.items():
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

# In the 3D PLOTTER SETUP section, after the BOA loops:

# Knee orientation marker
knee_position = [76.16, 1.4, 247.11]
knee_sphere = pv.Sphere(radius=6, center=knee_position)
plotter.add_mesh(knee_sphere, color='cyan', opacity=0.9)
plotter.add_point_labels(
    [knee_position],
    ['Knee ↑'],
    font_size=14,
    point_size=0,
    text_color='cyan',
    bold=True,
    shape_color='black',
    shape_opacity=0.8
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
    "Scale (relative to baseline):\nBlue = Too Tight\nGreen = Ideal\nRed = Too Loose",
    position=(0.02, 0.15),
    font_size=10,
    color='yellow',
    font='arial',
    shadow=True
)

def tare_callback():
    print("\n[TARE] 'T' key pressed!")
    sensor.tare()

plotter.add_key_event('t', tare_callback)
plotter.add_key_event('T', tare_callback)

import os

def on_window_close(obj, event):
    print("\nWindow closed — shutting down...")
    os._exit(0)

# Hook into VTK's DeleteEvent (fires when window is closed)
plotter.ren_win.AddObserver("DeleteEvent", on_window_close)

plotter.show(interactive_update=True, auto_close=False)

print("\n" + "="*50)
print("Visualization running!")
print("="*50 + "\n")


# === MAIN LOOP ===
try:
    while True:
        pressure_values = sensor.get_display()
        mesh.cell_data['colors'] = update_mesh_colors(pressure_values)
        plotter.update()
        time.sleep(0.1)

        if not plotter.ren_win:
            break

except KeyboardInterrupt:
    print("\nStopped by user")
except Exception as e:
    print(f"\nVisualization ended: {e}")
finally:
    try:
        plotter.close()
    except:
        pass
    print("Closed")
    os._exit(0)
