import pyvista as pv
mesh = pv.read('leg.stl')

picked_points = []

def pick_callback(point):
    print(f"Picked point: {point}")
    picked_points.append(point)

plotter = pv.Plotter()
plotter.add_mesh(mesh, color='lightblue')
plotter.enable_point_picking(callback=pick_callback, show_message=True)
print("Click on 4 locations where sensors will be placed, then close window")
plotter.show()

print("\nPatch centers to use:")
for i, pt in enumerate(picked_points[:4]):
    print(f"    [{pt[0]:.2f}, {pt[1]:.2f}, {pt[2]:.2f}],  # Patch {i+1}")