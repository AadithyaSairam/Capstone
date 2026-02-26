import pyvista as pv
import numpy as np
import matplotlib.pyplot as plt
import threading
import time
import tkinter as tk
from scipy.spatial import Delaunay
from sensor_sdk import SocketSensor


# === CONFIGURATION ===
sensor = SocketSensor(device_name="ESP32_LoadCells", threshold=20)


# === BOA REGION DEFINITIONS ===
boa_regions = {
0: {
    'name': 'BOA 1 (Front)',
    'position': [79.22101593, 12.75070763, 155.10850525],
        'zones': [
        # Zone 1
        np.array([
            [64.01, 5.64, 220.57],
            [64.01, 5.64, 220.57],
            [66.50, 5.11, 220.57],
            [69.06, 4.76, 220.57],
            [71.68, 4.58, 220.57],
            [74.36, 4.59, 220.57],
            [79.83, 5.11, 220.57],
            [79.83, 5.11, 220.57],
            [77.08, 4.77, 220.57],
            [82.59, 5.62, 220.57],
            [80.47, 3.81, 225.01],
            [83.30, 4.34, 225.01],
            [86.12, 5.03, 225.01],
            [87.12, 3.83, 229.51],
            [91.67, 6.85, 225.01],
            [94.37, 7.96, 225.01],
            [91.67, 6.85, 225.01],
            [92.78, 10.14, 216.17],
            [92.46, 10.98, 211.80],
            [94.37, 7.96, 225.01],
            [94.37, 7.96, 225.01],
            [92.46, 10.98, 211.80],
            [92.78, 10.14, 216.17],
            [92.51, 11.54, 207.45],
            [61.58, 6.33, 220.57],
            [56.84, 8.15, 220.57],
            [56.84, 8.15, 220.57],
            [52.20, 9.09, 225.01],
            [52.20, 9.09, 225.01],
            [47.66, 10.54, 229.51],
            [43.06, 13.62, 229.51],
            [47.60, 11.83, 225.01],
            [43.02, 14.88, 225.01],
            [43.02, 14.88, 225.01],
            [43.11, 16.13, 220.57],
            [43.37, 17.28, 216.17],
            [43.02, 14.88, 225.01],
            [43.02, 14.88, 225.01],
            [47.67, 13.15, 220.57],
            [52.23, 10.45, 220.57],
            [61.58, 6.33, 220.57],
            [64.00, 7.01, 216.17],
            [79.44, 6.36, 216.17],
            [82.14, 6.83, 216.17],
            [82.59, 5.62, 220.57],
            [68.93, 6.11, 216.17],
            [64.01, 5.64, 220.57],
            [61.62, 7.70, 216.17],
            [56.84, 8.15, 220.57],
            [52.23, 10.45, 220.57],
            [52.23, 10.45, 220.57],
            [52.42, 11.75, 216.17],
            [52.42, 11.75, 216.17],
            [52.78, 12.85, 211.80],
            [48.33, 15.41, 211.80],
            [48.33, 15.41, 211.80],
            [52.23, 10.45, 220.57],
            [48.33, 15.41, 211.80],
            [47.91, 14.38, 216.17],
            [48.33, 15.41, 211.80],
            [43.83, 18.23, 211.80],
            [57.27, 10.64, 211.80],
            [61.62, 7.70, 216.17],
            [56.97, 9.49, 216.17],
            [61.84, 8.88, 211.80],
            [64.19, 8.20, 211.80],
            [69.02, 7.29, 211.80],
            [74.10, 7.04, 211.80],
            [74.10, 5.90, 216.17],
            [76.75, 6.05, 216.17],
            [81.98, 7.86, 211.80],
            [87.27, 9.15, 211.80],
            [87.52, 8.21, 216.17],
            [88.08, 7.08, 220.57],
            [93.43, 9.10, 220.57],
            [93.43, 9.10, 220.57],
            [96.02, 10.31, 220.57],
            [98.53, 11.64, 220.57],
            [98.53, 11.64, 220.57],
            [97.83, 12.57, 216.17],
            [97.83, 12.57, 216.17],
            [100.23, 13.96, 216.17],
            [97.45, 13.31, 211.80],
            [97.45, 13.31, 211.80],
            [97.44, 13.79, 207.45],
            [97.44, 13.79, 207.45],
            [97.45, 13.31, 211.80],
            [92.51, 11.54, 207.45],
            [87.82, 10.15, 203.10],
            [87.38, 9.80, 207.45],
            [82.16, 8.59, 207.45],
            [76.95, 7.96, 207.45],
            [71.84, 7.93, 207.45],
            [64.58, 9.07, 207.45],
            [62.26, 9.75, 207.45],
            [57.75, 11.47, 207.45],
            [53.33, 13.63, 207.45],
            [54.04, 14.05, 203.10],
            [49.75, 16.50, 203.10],
            [45.44, 19.21, 203.10],
            [48.94, 16.13, 207.45],
            [48.94, 16.13, 207.45],
            [44.52, 18.88, 207.45],
            [45.44, 19.21, 203.10],
            [43.37, 17.28, 216.17],
            [43.37, 17.28, 216.17],
            [43.37, 17.28, 216.17],
            [43.83, 18.23, 211.80],
            [43.83, 18.23, 211.80],
            [44.52, 18.88, 207.45],
            [44.52, 18.88, 207.45],
            [43.02, 14.88, 225.01],
            [57.27, 10.64, 211.80],
        ]),
    ]
},

    1: {
        'name': 'BOA 2 (Side)',
        'position': [28.12449265, 48.21684265, 159.52259827],
        'zones': [
            np.array([
                [10, 30, 148], [45, 30, 148],
                [10, 65, 148], [45, 65, 148],
                [10, 30, 172], [45, 30, 172],
                [10, 65, 172], [45, 65, 172],
                [15, 48, 155], [40, 48, 165],
            ]),
        ]
    },
    2: {
        'name': 'BOA 3 (Back)',
        'position': [76.4567337, 108.86454773, 137.45446777],
        'zones': [
        # Zone 1
        np.array([
            [58.26, 109.94, 93.35],
            [60.70, 110.68, 93.35],
            [63.17, 111.27, 93.35],
            [68.16, 111.95, 93.35],
            [73.16, 111.95, 93.35],
            [75.64, 111.69, 93.35],
            [78.11, 111.27, 93.35],
            [80.55, 110.69, 93.35],
            [88.99, 108.27, 106.59],
            [84.13, 109.98, 106.59],
            [83.67, 110.10, 102.17],
            [78.72, 111.33, 102.17],
            [78.37, 111.38, 97.76],
            [89.54, 108.14, 111.00],
            [90.10, 107.92, 115.41],
            [90.63, 107.64, 119.82],
            [90.63, 107.64, 119.82],
            [93.00, 105.24, 159.52],
            [92.99, 106.51, 150.69],
            [92.85, 106.81, 146.28],
            [92.35, 106.92, 137.45],
            [91.59, 107.10, 128.64],
            [90.63, 107.64, 119.82],
            [91.59, 107.10, 128.64],
            [91.59, 107.10, 128.64],
            [90.63, 107.64, 119.82],
            [91.59, 107.10, 128.64],
            [92.64, 106.91, 141.87],
            [93.04, 105.92, 155.11],
            [91.59, 107.10, 128.64],
            [86.89, 108.11, 133.04],
            [92.35, 106.92, 137.45],
            [90.63, 107.64, 119.82],
            [90.63, 107.64, 119.82],
            [90.63, 107.64, 119.82],
            [91.59, 107.10, 128.64],
            [85.63, 109.06, 119.82],
            [86.51, 108.34, 128.64],
            [85.63, 109.06, 119.82],
            [86.51, 108.34, 128.64],
            [92.35, 106.92, 137.45],
            [96.43, 105.38, 128.64],
            [87.20, 108.01, 137.45],
            [87.61, 107.76, 146.28],
            [87.44, 107.94, 141.87],
            [87.70, 107.35, 150.69],
            [87.70, 106.59, 155.11],
            [87.63, 105.76, 159.52],
            [87.57, 105.45, 161.73],
            [82.00, 105.56, 161.73],
            [82.00, 105.56, 161.73],
            [76.35, 105.38, 161.73],
            [70.80, 105.39, 159.52],
            [70.71, 104.99, 161.73],
            [76.44, 105.77, 159.52],
            [82.08, 105.91, 159.52],
            [76.44, 105.77, 159.52],
            [65.25, 104.85, 159.52],
            [58.44, 110.03, 97.76],
            [58.64, 109.95, 102.17],
            [58.87, 109.74, 106.59],
            [59.11, 109.41, 111.00],
            [59.65, 108.52, 119.82],
            [59.65, 108.52, 119.82],
            [59.11, 109.41, 111.00],
            [60.12, 107.64, 128.64],
            [60.12, 107.64, 128.64],
            [60.28, 107.34, 133.04],
            [60.35, 107.16, 137.45],
            [60.35, 107.00, 141.87],
            [60.29, 106.70, 146.28],
            [60.19, 106.12, 150.69],
            [60.04, 105.15, 155.11],
            [59.86, 104.12, 159.52],
            [60.12, 107.64, 128.64],
            [60.12, 107.64, 128.64],
            [64.74, 109.65, 119.82],
            [65.30, 108.66, 128.64],
            [60.12, 107.64, 128.64],
            [60.12, 107.64, 128.64],
            [59.65, 108.52, 119.82],
            [59.11, 109.41, 111.00],
            [65.30, 108.66, 128.64],
            [64.74, 109.65, 119.82],
            [69.95, 110.27, 119.82],
            [75.21, 110.38, 119.82],
            [75.95, 109.40, 128.64],
            [75.21, 110.38, 119.82],
            [85.63, 109.06, 119.82],
            [85.63, 109.06, 119.82],
            [85.63, 109.06, 119.82],
            [81.28, 109.10, 128.64],
            [80.46, 109.97, 119.82],
            [85.63, 109.06, 119.82],
            [90.63, 107.64, 119.82],
            [90.63, 107.64, 119.82],
            [85.63, 109.06, 119.82],
            [85.63, 109.06, 119.82],
            [90.63, 107.64, 119.82],
            [90.63, 107.64, 119.82],
            [84.63, 109.75, 111.00],
            [85.63, 109.06, 119.82],
            [82.22, 107.76, 150.69],
            [82.19, 106.88, 155.11],
            [76.58, 106.83, 155.11],
            [70.96, 106.50, 155.11],
            [65.43, 105.95, 155.11],
            [65.56, 106.97, 150.69],
            [76.65, 107.81, 150.69],
            [82.18, 108.28, 146.28],
            [82.07, 108.52, 141.87],
            [81.88, 108.65, 137.45],
            [81.61, 108.81, 133.04],
            [76.46, 108.86, 137.45],
            [76.60, 108.69, 141.87],
            [76.66, 108.40, 146.28],
            [71.07, 107.53, 150.69],
            [71.12, 108.16, 146.28],
            [65.64, 107.59, 146.28],
            [65.67, 107.92, 141.87],
            [71.01, 108.67, 137.45],
            [71.01, 108.67, 137.45],
            [76.24, 109.06, 133.04],
            [70.85, 108.89, 133.04],
            [65.50, 108.31, 133.04],
            [65.62, 108.10, 137.45],
            [71.10, 108.48, 141.87],
            [70.60, 109.25, 128.64],
            [75.95, 109.40, 128.64],
            [79.56, 110.83, 111.00],
            [90.10, 107.92, 115.41],
            [80.46, 109.97, 119.82],
            [59.11, 109.41, 111.00],
            [66.67, 111.04, 111.00],
            [69.24, 111.29, 111.00],
            [69.95, 110.27, 119.82],
            [74.41, 111.35, 111.00],
            [75.64, 111.69, 93.35],
            [73.68, 111.95, 102.17],
            [73.39, 112.04, 97.76],
            [71.15, 112.02, 102.17],
            [68.62, 111.93, 102.17],
            [79.12, 111.14, 106.59],
            [73.68, 111.95, 102.17],
            [71.82, 111.40, 111.00],
            [73.68, 111.95, 102.17],
            [73.68, 111.95, 102.17],
            [73.68, 111.95, 102.17],
            [74.41, 111.35, 111.00],
            [71.82, 111.40, 111.00],
            [76.99, 111.17, 111.00],
            [79.56, 110.83, 111.00],
            [84.63, 109.75, 111.00],
            [89.54, 108.14, 111.00],
            [84.63, 109.75, 111.00],
            [84.63, 109.75, 111.00],
            [80.46, 109.97, 119.82],
            [84.63, 109.75, 111.00],
            [75.21, 110.38, 119.82],
            [85.63, 109.06, 119.82],
            [84.63, 109.75, 111.00],
            [85.63, 109.06, 119.82],
            [80.46, 109.97, 119.82],
            [69.24, 111.29, 111.00],
            [63.84, 111.00, 106.59],
            [64.12, 110.63, 111.00],
            [64.12, 110.63, 111.00],
            [73.68, 111.95, 102.17],
            [79.12, 111.14, 106.59],
            [73.68, 111.95, 102.17],
            [63.36, 111.34, 97.76],
            [63.36, 111.34, 97.76],
            [70.66, 112.04, 93.35],
            [73.68, 111.95, 102.17],
            [68.62, 111.93, 102.17],
            [70.88, 112.12, 97.76],
            [68.37, 112.03, 97.76],
            [63.58, 111.25, 102.17],
            [66.09, 111.67, 102.17],
            [78.37, 111.38, 97.76],
            [83.67, 110.10, 102.17],
            [74.41, 111.35, 111.00],
            [59.11, 109.41, 111.00],
        ]),
    ]
    },
    3: {
        'name': 'BOA 4 (Top)',
        'position': [118.10018921, 54.5916481, 130.84025574],
        'zones': [
            np.array([
                [103, 38, 118], [133, 38, 118],
                [103, 72, 118], [133, 72, 118],
                [103, 38, 143], [133, 38, 143],
                [103, 72, 143], [133, 72, 143],
                [118, 54, 125], [118, 54, 138],
            ]),
        ]
    },
}


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
            pressure_values = sensor.get_display()

            if sensor.using_real_data:
                conn_indicator.config(fg='#33ff33')
                conn_label.config(text="Bluetooth Connected", fg='#33ff33')
            else:
                conn_indicator.config(fg='orange')
                conn_label.config(text="Manual Control", fg='orange')

            for i, (p_label, a_label, frame) in enumerate(boa_labels):
                p_label.config(text=f"Pressure: {pressure_values[i]:+6.1f}")

                if sensor.has_capture:
                    action, color_rgb = sensor.get_recommendation(i)

                    color_hex = '#{:02x}{:02x}{:02x}'.format(
                        int(color_rgb[0]*255),
                        int(color_rgb[1]*255),
                        int(color_rgb[2]*255)
                    )
                    a_label.config(text=action, fg=color_hex)

                    deviation = sensor.get_deviation(i)

                    if deviation > sensor.threshold:
                        frame.config(bg='#4d2626')
                        p_label.config(bg='#4d2626')
                        a_label.config(bg='#4d2626')
                    elif deviation < -sensor.threshold:
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
    colors[:] = [0.8, 0.8, 0.8]  # Gray for unassigned regions

    baseline = sensor.get_baseline()

    for i in range(4):
        mask = mesh['region'] == i
        if np.any(mask):
            deviation = pressure_values[i] - baseline[i]
            normalized = (deviation + 50) / 100  # -50→0(blue), 0→0.5(green), +50→1(red)
            normalized = np.clip(normalized, 0, 1)

            colormap = plt.get_cmap('jet')
            rgba = colormap(normalized)
            colors[mask] = rgba[:3]

    return colors


# === STARTUP ===
print("="*50)
print("Loading configuration...")
sensor.load_baseline()
print("="*50)

print("Starting Bluetooth connection...")
sensor.connect()
print("Waiting for ESP32...")
time.sleep(15)

print("Launching simulation control...")
sim_thread = threading.Thread(target=create_simulation_panel, daemon=True)
sim_thread.start()
time.sleep(0.5)
sensor.start_manual_stream()

print("Launching control panel...")
control_thread = threading.Thread(target=create_control_panel, daemon=True)
control_thread.start()
time.sleep(1)


# === LOAD 3D MODEL ===
print("Loading 3D model...")
mesh = pv.read('leg.stl')

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

# Check if your picked points are even in the right coordinate space
print(f"\nYour BOA 1 zone X range: 49.3 → 97.8")
print(f"Your BOA 1 zone Y range: -104 → 12")
print(f"Your BOA 1 zone Z range: 199 → 222")

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
    plotter.close()
    print("Closed")
