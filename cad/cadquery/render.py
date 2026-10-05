"""Quick shaded previews (matplotlib, no GPU needed) -> docs/renders/*.png"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from foldable_laptop import Design, build_all, rotate_lid, COLORS

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "docs", "renders")
os.makedirs(OUT, exist_ok=True)
LIGHT = np.array([0.4, -0.6, 0.8]); LIGHT /= np.linalg.norm(LIGHT)


def tris(shape, tol=0.25):
    vs, fs = shape.val().tessellate(tol, 0.2)
    v = np.array([(p.x, p.y, p.z) for p in vs])
    return v[np.array(fs)]


def view_matrix(elev, azim):
    """Orthographic camera; azim/elev in degrees like matplotlib."""
    a, e = np.radians(azim), np.radians(elev)
    fwd = -np.array([np.cos(e) * np.cos(a), np.cos(e) * np.sin(a), np.sin(e)])  # camera looks along fwd
    right = np.cross(fwd, [0, 0, 1.0]); right /= np.linalg.norm(right)
    up = np.cross(right, fwd)
    return np.stack([right, up, -fwd])  # rows: screen x, screen y, depth (towards viewer)


def draw(items, fname, elev=24, azim=-58, title=None, size=(1400, 1000)):
    """Tiny z-buffer rasterizer (no GPU / display needed)."""
    Wp, Hp = size
    M = view_matrix(elev, azim)
    light = M.T @ np.array([-0.35, 0.55, 0.75]); light /= np.linalg.norm(light)
    data = []
    for shp, col, _ in items:
        t = tris(shp)
        n = np.cross(t[:, 1] - t[:, 0], t[:, 2] - t[:, 0])
        n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-12
        data.append((t @ M.T, n, np.array(col)))
    allp = np.vstack([d_[0].reshape(-1, 3) for d_ in data])
    mn, mx = allp.min(0), allp.max(0)
    scale = 0.86 * min(Wp / (mx[0] - mn[0]), Hp / (mx[1] - mn[1]))
    off = np.array([Wp / 2, Hp / 2]) - scale * (mn[:2] + mx[:2]) / 2
    zbuf = np.full((Hp, Wp), -np.inf)
    img = np.ones((Hp, Wp, 3))
    obj = np.full((Hp, Wp), -1)
    for oi, (p, n, col) in enumerate(data):
        P = p.copy(); P[:, :, :2] = P[:, :, :2] * scale + off
        P[:, :, 1] = Hp - P[:, :, 1]
        shade = 0.35 + 0.65 * np.abs(n @ light)
        for tri, sh in zip(P, shade):
            x0, y0 = np.floor(tri[:, :2].min(0)).astype(int)
            x1, y1 = np.ceil(tri[:, :2].max(0)).astype(int)
            x0, y0 = max(x0, 0), max(y0, 0); x1, y1 = min(x1, Wp - 1), min(y1, Hp - 1)
            if x1 < x0 or y1 < y0:
                continue
            (ax, ay, az), (bx, by, bz), (cx, cy, cz) = tri
            den = (by - cy) * (ax - cx) + (cx - bx) * (ay - cy)
            if abs(den) < 1e-9:
                continue
            xs, ys = np.meshgrid(np.arange(x0, x1 + 1) + 0.5, np.arange(y0, y1 + 1) + 0.5)
            l1 = ((by - cy) * (xs - cx) + (cx - bx) * (ys - cy)) / den
            l2 = ((cy - ay) * (xs - cx) + (ax - cx) * (ys - cy)) / den
            l3 = 1 - l1 - l2
            m = (l1 >= -1e-6) & (l2 >= -1e-6) & (l3 >= -1e-6)
            if not m.any():
                continue
            z = l1 * az + l2 * bz + l3 * cz
            sub = zbuf[y0:y1 + 1, x0:x1 + 1]
            m &= z > sub
            sub[m] = z[m]
            img[y0:y1 + 1, x0:x1 + 1][m] = np.clip(col * sh, 0, 1)
            obj[y0:y1 + 1, x0:x1 + 1][m] = oi
    # outlines: depth jumps and object boundaries
    zf = np.where(np.isfinite(zbuf), zbuf, mn[2] - 50)
    gx = np.abs(np.diff(zf, axis=1, prepend=zf[:, :1])); gy = np.abs(np.diff(zf, axis=0, prepend=zf[:1]))
    ob = (np.diff(obj, axis=1, prepend=obj[:, :1]) != 0) | (np.diff(obj, axis=0, prepend=obj[:1]) != 0)
    edge = (np.maximum(gx, gy) > 1.5 / scale * 3) | ob
    img[edge] = img[edge] * 0.25
    fig = plt.figure(figsize=(Wp / 140, Hp / 140), dpi=140)
    ax = fig.add_axes([0, 0, 1, 1]); ax.imshow(img); ax.set_axis_off()
    if title:
        ax.text(20, 40, title, fontsize=14)
    fig.savefig(os.path.join(OUT, fname), facecolor="white")
    plt.close(fig)
    print("wrote", fname)


d = Design()
parts, dummies = build_all(d)
lidn = {"lid_bezel", "lid_back", "display"}


def scene(angle, show_dummies=True, explode=0.0, hide=()):
    items = []
    for name, shp in {**parts, **(dummies if show_dummies else {})}.items():
        if name in hide:
            continue
        s = rotate_lid(d, shp, angle) if name in lidn else shp
        col = COLORS.get(name, COLORS["base_top"])
        if explode:
            dz = {"base_bottom": -1, "powerbank": -1, "pi5_stack": -0.5, "lid_bezel": 1, "display": 1.5, "lid_back": 2.5}.get(name, 0)
            if name.startswith("knuckle"):
                dz = 0.6
            s = s.translate((0, 0, dz * explode))
        items.append((s, col, 1.0))
    return items


draw(scene(0), "closed.png", title="Closed (lid magnets latch)")
draw(scene(110), "open_110.png", title="Open 110 degrees")
draw(scene(110), "open_110_rear.png", azim=135, elev=20, title="Rear: hinge knuckles + cable channel")
draw(scene(0, explode=40, hide=("keyboard",)), "exploded.png", elev=18, title="Exploded (closed position)")
draw(scene(0, hide=("lid_bezel", "lid_back", "display", "keyboard", "base_top") + tuple(k for k in parts if k.startswith("knuckle"))),
     "base_layout.png", elev=62, azim=-90, title="Base bottom: power bank (front), Pi 5 + HAT + IO adapter (rear left)")
draw([(parts["base_top"], COLORS["base_top"], 1.0)] + [(parts[k], (0.8, 0.4, 0.1), 1.0) for k in parts if k.startswith("knuckle")],
     "base_top.png", elev=55, azim=-70, title="base_top: keyboard pocket, fan grill, cable slot")
