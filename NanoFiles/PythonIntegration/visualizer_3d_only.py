# visualizer_usb.py  —  USB serial, 3D heat map only (no Tkinter)
import pyvista as pv
import numpy as np
import matplotlib.pyplot as plt
import time
import os

from sensor_sdk_serial import SerialSensor
from regions import boa_regions, build_regions   # ← Delaunay version
from utils import resource_path

# ── CONFIG ────────────────────────────────────────────────────────────────
sensor = SerialSensor(device_name="ESP32_LoadCells", threshold=3, sample_count=20)
CMAP   = plt.get_cmap("jet")

# ── LOAD + REFINE MESH ────────────────────────────────────────────────────
print("Loading 3D model...")
mesh = pv.read(resource_path("leg.stl"))
mesh = mesh.clean()
mesh = mesh.subdivide(2, subfilter="loop")
cellcenters = mesh.cell_centers().points
print(f"Mesh: {mesh.n_cells} cells")

# ── ASSIGN REGION IDs ─────────────────────────────────────────────────────
print("Building regions...")
region_ids = build_regions(cellcenters)   # Delaunay — correct zone mapping
mesh["region"] = region_ids

# ── COLOR MAPPING ─────────────────────────────────────────────────────────
def update_mesh_colors(pressure_values):
    colors   = np.full((mesh.n_cells, 3), 0.25)   # dark grey = unassigned
    baseline = sensor.get_baseline()
    for i in range(4):
        mask = (region_ids == i)
        if not np.any(mask):
            continue
        deviation  = pressure_values[i] - baseline[i]
        normalized = np.clip((-deviation + 25) / 50.0, 0.0, 1.0)
        rgba       = CMAP(normalized)
        colors[mask] = rgba[:3]
    return colors

# ── CONNECT ───────────────────────────────────────────────────────────────
print("Connecting via USB serial...")
connected = sensor.connect()
if not connected:
    print("⚠ Could not connect — showing grey model. Check USB cable.")
else:
    print("✓ Connected")

sensor.load_baseline()

# ── PLOTTER SETUP ─────────────────────────────────────────────────────────
print("Creating visualization...")
plotter = pv.Plotter(title="Prosthetic Socket — USB Heat Map")

mesh.cell_data["colors"] = update_mesh_colors([0.0, 0.0, 0.0, 0.0])
plotter.add_mesh(mesh, scalars="colors", rgb=True,
                 show_edges=False, lighting=True)

# Region labels
for _, info in boa_regions.items():
    sphere = pv.Sphere(radius=5, center=info["position"])
    plotter.add_mesh(sphere, color="yellow", opacity=0.9)
    plotter.add_point_labels(
        [info["position"]], [info["name"]],
        font_size=12, point_size=0,
        text_color="white", bold=True,
        shape_color="black", shape_opacity=0.7,
    )

# Knee marker
knee_pos = (76.16, 1.4, 247.11)
plotter.add_mesh(pv.Sphere(radius=6, center=knee_pos), color="cyan", opacity=0.9)
plotter.add_point_labels(
    [knee_pos], ["Knee"],
    font_size=14, point_size=0,
    text_color="cyan", bold=True,
    shape_color="black", shape_opacity=0.8,
)

plotter.add_text("3D Pressure Heat Map  [USB]",
                 position="upper_edge", font_size=14,
                 color="white", font="arial", shadow=True)
plotter.add_text("← Too Tight   Ideal   Too Loose →",
                 position=(0.02, 0.05), font_size=10,
                 color="yellow", font="arial", shadow=True)

# T → tare,  Q → quit
def tare_callback():
    print("Taring...")
    sensor.tare()

def quit_callback():
    print("Quit.")
    os._exit(0)

plotter.add_key_event("t", tare_callback)
plotter.add_key_event("T", tare_callback)
plotter.add_key_event("q", quit_callback)
plotter.add_key_event("Q", quit_callback)

def on_close(obj, event):
    print("Window closed.")
    os._exit(0)

plotter.ren_win.AddObserver("DeleteEvent", on_close)

# ── LIVE UPDATE LOOP ──────────────────────────────────────────────────────
plotter.show(interactive_update=True, auto_close=False)
print("Running — T to tare, Q to quit")

try:
    while True:
        pressures = sensor.get_display()
        mesh.cell_data["colors"] = update_mesh_colors(pressures)
        plotter.update()
        time.sleep(0.1)
        if not plotter.ren_win:
            break
except KeyboardInterrupt:
    pass
finally:
    try:
        plotter.close()
    except Exception:
        pass
