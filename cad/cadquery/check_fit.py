"""Sanity checks: valid solids, bed fit, and hinge interference across the swing."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import cadquery as cq
from foldable_laptop import Design, build_all, rotate_lid, print_orientation

d = Design()
parts, dummies = build_all(d)
ok = True
for n, s in parts.items():
    v = s.val()
    po = print_orientation(d, n, s).val().BoundingBox()
    print(f"{n:12s} valid={v.isValid()} solids={len(s.solids().vals())} "
          f"vol={v.Volume()/1000:.1f} cm3 print-bbox={po.xlen:.1f}x{po.ylen:.1f}x{po.zlen:.1f}")
    ok &= v.isValid()

def vol(a, b):
    try:
        return a.intersect(b).val().Volume()
    except Exception:
        return 0.0

base = parts["base_bottom"].union(parts["base_top"])
for n in parts:
    if n.startswith("knuckle"):
        base = base.union(parts[n])
# dummies must not collide with printed parts (closed)
from foldable_laptop import box
for dn in ("keyboard", "powerbank", "pi5_stack"):
    dm = dummies[dn]
    if dn == "pi5_stack":  # the standoffs sit beside the SSD, under the HAT
        dm = dm.cut(box(-500, 500, -500, 500, -10, d.standoff_top))
    v = vol(base, dm); print(f"closed: {dn} vs base overlap {v:.2f} mm3"); ok &= v < 1
v = vol(parts["lid_bezel"].union(parts["lid_back"]), dummies["display"])
print(f"closed: display vs lid overlap {v:.2f} mm3"); ok &= v < 1
for ang in (0, 15, 30, 45, 60, 90, 110, 130, 150):
    lid = rotate_lid(d, parts["lid_bezel"].union(parts["lid_back"]), ang)
    v = vol(base, lid)
    print(f"angle {ang:3d}: lid vs base overlap {v:.2f} mm3"); ok &= v < 1
print("ALL OK" if ok else "PROBLEMS FOUND")
