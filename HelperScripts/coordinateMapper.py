"""
region_mapper.py
─────────────────────────────────────────────────────
Helper tool to interactively pick points on leg.stl
and generate zone coordinate arrays ready to paste
into visualizer.py boa_regions.

Controls:
  P         → pick point under cursor
  U         → undo last picked point
  1/2/3/4   → switch active BOA region
  N         → start a new zone within current region
  C         → print collected coordinates to terminal
  Q         → quit and print final output
─────────────────────────────────────────────────────
"""

import pyvista as pv
import numpy as np


# ── State ─────────────────────────────────────────
MESH_FILE = 'leg.stl'

BOA_NAMES = {
    1: 'BOA 1 (Front)',
    2: 'BOA 2 (Side)',
    3: 'BOA 3 (Back)',
    4: 'BOA 4 (Top)',
}

BOA_COLORS = {
    1: 'red',
    2: 'blue',
    3: 'green',
    4: 'orange',
}

# All collected data: { boa_index: [ [zone_points], [zone_points], ... ] }
collected = {1: [[]], 2: [[]], 3: [[]], 4: [[]]}
active_boa = [1]   # mutable so lambdas can modify it
markers = []       # pyvista actors for picked point spheres


# ── Helpers ───────────────────────────────────────
def current_zone():
    return collected[active_boa[0]][-1]


def print_coords():
    """Print current collected zones formatted for copy-paste into visualizer.py"""
    print("\n" + "="*60)
    print("  COPY THIS INTO boa_regions IN visualizer.py")
    print("="*60)
    for boa_idx in range(1, 5):
        zones = collected[boa_idx]
        non_empty = [z for z in zones if len(z) >= 4]
        if not non_empty:
            continue
        print(f"\n    # {BOA_NAMES[boa_idx]}")
        print(f"    'zones': [")
        for z_idx, zone in enumerate(non_empty):
            pts = np.array(zone)
            print(f"        # Zone {z_idx + 1}")
            print(f"        np.array([")
            for pt in pts:
                print(f"            [{pt[0]:.2f}, {pt[1]:.2f}, {pt[2]:.2f}],")
            print(f"        ]),")
        print(f"    ]")
    print("="*60 + "\n")


def update_status():
    boa = active_boa[0]
    zone_idx = len(collected[boa])
    pt_count = len(current_zone())
    total_pts = sum(len(z) for z in collected[boa])
    plotter.add_text(
        f"Active: {BOA_NAMES[boa]}  |  Zone {zone_idx}  |  "
        f"Points this zone: {pt_count}  |  Total: {total_pts}\n"
        f"Keys: P=Pick  U=Undo  1-4=Switch BOA  N=New Zone  C=Print  Q=Quit",
        position='upper_edge',
        font_size=10,
        color=BOA_COLORS[boa],
        name='status'  # reuse same text actor
    )
    plotter.render()


# ── Callbacks ─────────────────────────────────────
def on_pick(picked_point):
    """Find the closest actual mesh point to where we clicked"""
    # Find the closest mesh vertex to the picked point
    mesh_points = mesh.points
    distances = np.linalg.norm(mesh_points - picked_point, axis=1)
    closest_idx = np.argmin(distances)
    pt = mesh_points[closest_idx]
    pt = [round(float(pt[0]), 2),
          round(float(pt[1]), 2),
          round(float(pt[2]), 2)]

    current_zone().append(pt)
    print(f"  [{BOA_NAMES[active_boa[0]]}] Zone {len(collected[active_boa[0]])} "
          f"→ Snapped to mesh: {pt}  ({len(current_zone())} pts)")

    sphere = pv.Sphere(radius=2.5, center=pt)
    actor = plotter.add_mesh(sphere,
                             color=BOA_COLORS[active_boa[0]],
                             opacity=0.9)
    markers.append((active_boa[0], len(collected[active_boa[0]]) - 1, actor))
    update_status()


def undo_last():
    zone = current_zone()
    if zone:
        removed = zone.pop()
        print(f"  Undid point: {removed}")
        # Remove last marker for this boa/zone
        for i in reversed(range(len(markers))):
            b, z, actor = markers[i]
            if b == active_boa[0] and z == len(collected[active_boa[0]]) - 1:
                plotter.remove_actor(actor)
                markers.pop(i)
                break
    else:
        print("  Nothing to undo in current zone")
    update_status()


def new_zone():
    boa = active_boa[0]
    if len(current_zone()) < 4:
        print(f"  ⚠ Need at least 4 points before starting a new zone (have {len(current_zone())})")
        return
    collected[boa].append([])
    print(f"  Started new zone {len(collected[boa])} for {BOA_NAMES[boa]}")
    update_status()


def switch_boa(idx):
    active_boa[0] = idx
    print(f"\n  Switched to {BOA_NAMES[idx]}")
    update_status()


def quit_and_print():
    print_coords()
    plotter.close()

from scipy.interpolate import griddata

def fill_gaps():
    """
    Auto-fills gaps in current zone by interpolating a dense grid
    from existing picked points and snapping each to nearest mesh vertex.
    """
    zone = current_zone()
    if len(zone) < 6:
        print("  ⚠ Need at least 6 points to fill gaps")
        return

    pts = np.array(zone)
    print(f"  Filling gaps from {len(pts)} existing points...")

    # Build a dense grid over the X/Z extent of the picked region
    x_min, x_max = pts[:,0].min(), pts[:,0].max()
    z_min, z_max = pts[:,2].min(), pts[:,2].max()

    # Create a fine grid of X/Z positions (50x50 = up to 2500 candidate points)
    grid_x, grid_z = np.meshgrid(
        np.linspace(x_min, x_max, 50),
        np.linspace(z_min, z_max, 50)
    )

    # Interpolate Y values across the grid from existing points
    grid_y = griddata(
        pts[:, [0, 2]],   # known X/Z
        pts[:, 1],        # known Y
        (grid_x, grid_z), # query X/Z grid
        method='linear'
    )

    # Flatten and remove NaN (outside convex hull of known points)
    grid_pts = np.column_stack([
        grid_x.ravel(),
        grid_y.ravel(),
        grid_z.ravel()
    ])
    grid_pts = grid_pts[~np.isnan(grid_pts).any(axis=1)]

    # Snap each grid point to nearest mesh vertex
    mesh_points = mesh.points
    added = 0
    for gp in grid_pts:
        distances = np.linalg.norm(mesh_points - gp, axis=1)
        closest_idx = np.argmin(distances)
        pt = mesh_points[closest_idx]
        pt_list = [round(float(pt[0]), 2),
                   round(float(pt[1]), 2),
                   round(float(pt[2]), 2)]

        # Only add if not already in zone (avoid duplicates)
        if pt_list not in zone:
            zone.append(pt_list)
            sphere = pv.Sphere(radius=1.5, center=pt)
            actor = plotter.add_mesh(sphere,
                                     color=BOA_COLORS[active_boa[0]],
                                     opacity=0.5)
            markers.append((active_boa[0],
                            len(collected[active_boa[0]]) - 1,
                            actor))
            added += 1

    print(f"  ✓ Added {added} interpolated points — zone now has {len(zone)} total")
    update_status()






# ── Setup Plotter ─────────────────────────────────
print("Loading mesh...")
mesh = pv.read(MESH_FILE)
mesh = mesh.clean()

plotter = pv.Plotter()
plotter.add_mesh(mesh,
                 color='lightgray',
                 opacity=0.85,
                 pickable=True,
                 show_edges=False,
                 lighting=True)

# Axis indicator
plotter.add_axes()
plotter.add_text(
    "Loading...",
    position='upper_edge',
    font_size=10,
    color='white',
    name='status'
)

# ── Key Bindings ──────────────────────────────────
plotter.enable_surface_point_picking(
    callback=on_pick,
    show_message=False,
    pickable_window=False,
    show_point=False       # we draw our own colored spheres
)

plotter.add_key_event('u', undo_last)
plotter.add_key_event('U', undo_last)
plotter.add_key_event('n', new_zone)
plotter.add_key_event('N', new_zone)
plotter.add_key_event('c', print_coords)
plotter.add_key_event('C', print_coords)
plotter.add_key_event('q', quit_and_print)
plotter.add_key_event('Q', quit_and_print)
plotter.add_key_event('1', lambda: switch_boa(1))
plotter.add_key_event('2', lambda: switch_boa(2))
plotter.add_key_event('3', lambda: switch_boa(3))
plotter.add_key_event('4', lambda: switch_boa(4))
# Add this key binding with the others:
plotter.add_key_event('f', fill_gaps)
plotter.add_key_event('F', fill_gaps)

update_status()

print("\n" + "="*60)
print("  REGION MAPPER READY")
print("="*60)
print("  P         → pick point under cursor")
print("  U         → undo last point")
print("  1/2/3/4   → switch active BOA region")
print("  N         → new zone within current region")
print("  C         → print coordinates to terminal")
print("  Q         → quit and print final output")
print("="*60 + "\n")

plotter.show()
