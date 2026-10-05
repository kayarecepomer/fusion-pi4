"""
Foldable PiDeck remix: a clamshell "small laptop" that reuses the PiDeck parts.

Parametric CadQuery model. Run:

    python cad/cadquery/foldable_laptop.py              # builds + exports everything
    python cad/cadquery/foldable_laptop.py --angle 110  # open angle for the assembly

Outputs follow the repo layout: cad/step/<part>.step (plus foldable-assembly-
closed/open.step) and stl/<part>.stl in print orientation.
STEP files import straight into Autodesk Fusion (Insert > Insert Mesh is for STL;
use File > Open or Upload for STEP to get editable B-rep bodies).

Coordinate system (assembly, lid closed):
    X = width  (left -> right, centred on 0)
    Y = depth  (front edge y=0 -> hinge side y=D)
    Z = height (desk z=0 -> up)

All dimensions in mm. Every number that comes from a bought part lives in the
PARTS block so measured values can be dropped in without touching geometry code.
"""

from __future__ import annotations

import argparse
import math
import os
from dataclasses import dataclass, field

import cadquery as cq

# --------------------------------------------------------------------------
# Bought parts (from the PiDeck BOM). Replace with caliper measurements.
# --------------------------------------------------------------------------


@dataclass
class Parts:
    # Sizes marked STEP were measured from PiDeck V1's own assembly
    # (Pi_Deck_RaspberryPi5.step); see docs/components.md.

    # Rii X1 mini keyboard, rounded-edge version (STEP envelope)
    kb_w: float = 179.4
    kb_d: float = 64.9
    kb_h: float = 13.9

    # 7" IPS touch LCD module, envelope incl. driver board (STEP)
    disp_w: float = 166.0
    disp_h: float = 124.2
    disp_t: float = 14.1
    disp_hole_dx: float = 157.0  # 4x d3.3 mounting holes (STEP)
    disp_hole_dy: float = 114.9
    # visible area: NOT in the STEP (one solid). 1024x600 7" panels are
    # ~154.2 x 86; glass is 165.8 x 100.8. Assumed centred.
    active_w: float = 154.2
    active_h: float = 86.0
    active_dx: float = 0.0
    active_dy: float = 0.0

    # Raspberry Pi 5 + Waveshare NVMe HAT (under the Pi) (STEP). PiDeck's
    # Waveshare IO adapter is NOT used: short right-angle micro-HDMI / USB-C
    # cables replace it, which saves ~35 mm of base depth.
    pi_w: float = 90.1  # incl. USB/Ethernet overhang
    pi_overhang: float = 5.1
    pi_board_w: float = 85.0
    pi_board_d: float = 56.0
    pi_d: float = 57.7
    pi_stack_h: float = 26.1  # SSD bottom -> top of USB/Ethernet
    pi_board_z: float = 4.6  # Pi board bottom above stack bottom
    pi_hole_dx: float = 58.0
    pi_hole_dy: float = 49.0
    pi_hole_inset: float = 3.5

    # Power bank: Anker PowerCore III Wireless 10K (STEP)
    bat_w: float = 152.0
    bat_d: float = 69.0
    bat_h: float = 19.5

    # Fasteners / hardware reused from the PiDeck kit
    m25_clear: float = 2.8
    m25_csk_d: float = 5.0  # M2.5 countersunk head diameter
    insert_d: float = 3.4  # hole for M2.5 x 3.5 x 4 heat-set insert
    insert_l: float = 4.5
    magnet_d: float = 5.0
    magnet_t: float = 2.0
    m3_clear: float = 3.3
    m3_tight: float = 3.0  # base knuckle bore: snug, gives hinge friction
    m3_nut_af: float = 5.6  # nut across flats + clearance
    m3_nut_t: float = 2.6
    fan_size: float = 40.0
    fan_hole_pitch: float = 32.0
    button: float = 6.0  # 6x6 tact switch


@dataclass
class Design:
    p: Parts = field(default_factory=Parts)

    # Overall footprint (lid and base share it)
    W: float = 186.0  # keyboard 179.4 + clearance + walls
    D: float = 154.0  # set by the lid: 124.2 screen + hinge zone

    wall: float = 2.5
    floor: float = 2.0
    deck: float = 2.0  # top plate thickness of base
    clr: float = 0.4  # general fit clearance
    kb_clr: float = 0.6

    # Lid
    bezel_t: float = 2.0
    back_t: float = 2.0
    disp_front_margin: float = 8.0  # lid front edge -> display edge

    # Pi block sits this far in from the left wall so plugs fit (port recess)
    port_gap: float = 12.0

    # Hinge: 3 knuckles per side (base | lid | base), M3 bolt as the pin
    knuckle_base_l: float = 10.0
    knuckle_lid_l: float = 12.0
    knuckle_gap: float = 0.4

    # Cable channel through the middle of the hinge (flat FPC HDMI ribbon)
    cable_w: float = 26.0
    cable_slot: float = 6.0
    cable_x: float = -10.0  # centre of the channel, right above the Pi's micro-HDMI ports

    fillet_r: float = 3.0

    # ---- derived -------------------------------------------------------
    @property
    def Hs(self) -> float:
        """Split height between base_bottom and base_top (top of battery bay)."""
        return self.floor + self.p.bat_h + 1.0

    @property
    def kb_floor_t(self) -> float:
        return 1.5

    @property
    def H(self) -> float:
        """Base height: bay + keyboard tub floor + keyboard (flush)."""
        return self.Hs + self.kb_floor_t + self.p.kb_h + 0.3

    @property
    def Tl(self) -> float:
        """Lid thickness."""
        return self.bezel_t + self.p.disp_t + 0.5 + self.back_t

    @property
    def R(self) -> float:
        return self.Tl / 2.0

    @property
    def axis_y(self) -> float:
        return self.D - self.R

    @property
    def axis_z(self) -> float:
        return self.H + self.R

    # keyboard pocket (front of the deck)
    @property
    def kb_y0(self) -> float:
        return 9.0

    # battery bay: under the keyboard
    @property
    def bay_y0(self) -> float:
        return self.wall + 0.5

    @property
    def bay_y1(self) -> float:
        return self.bay_y0 + self.p.bat_d + 1.0

    # Pi + HAT block: rear-left, right behind the keyboard tub. USB/Ethernet
    # face the left wall; the micro-HDMI/USB-C edge faces the hinge, with a
    # gap for right-angle plugs and the display ribbon.
    @property
    def pi_x0(self) -> float:
        """x of the port end (USB/Ethernet face)."""
        return -self.W / 2 + self.wall + self.port_gap

    @property
    def pi_y0(self) -> float:
        """Front edge of the Pi envelope (just behind the keyboard tub)."""
        return self.kb_y0 + self.p.kb_d + 2 * self.kb_clr + 2.0 + 1.0

    @property
    def pi_y1(self) -> float:
        """Rear edge (micro-HDMI / USB-C side)."""
        return self.pi_y0 + self.p.pi_d

    @property
    def plug_gap(self) -> float:
        return self.D - self.wall - self.pi_y1

    @property
    def pi_z0(self) -> float:
        """Bottom of the stack (SSD underside)."""
        return self.floor + 4.0

    @property
    def standoff_top(self) -> float:
        """HAT/Pi mounting plane (just above the SSD)."""
        return self.pi_z0 + 3.5

    def knuckle_ranges(self):
        """x-ranges of base and lid knuckles for both sides."""
        b, l, g, W = self.knuckle_base_l, self.knuckle_lid_l, self.knuckle_gap, self.W
        base, lid = [], []
        for s in (1, -1):
            outer = (W / 2 - b, W / 2)
            lidk = (W / 2 - b - g - l, W / 2 - b - g)
            inner = (W / 2 - 2 * b - 2 * g - l, W / 2 - b - 2 * g - l)
            for r in (outer, inner):
                base.append(tuple(sorted((s * r[0], s * r[1]))))
            lid.append(tuple(sorted((s * lidk[0], s * lidk[1]))))
        return base, lid


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------


def box(x0, x1, y0, y1, z0, z1) -> cq.Workplane:
    return (
        cq.Workplane("XY")
        .box(x1 - x0, y1 - y0, z1 - z0, centered=False)
        .translate((x0, y0, z0))
    )


def xcyl(r, x0, x1, y, z) -> cq.Workplane:
    """Cylinder along X."""
    return (
        cq.Workplane("YZ")
        .circle(r)
        .extrude(x1 - x0)
        .translate((x0, y, z))
    )


def zcyl(r, x, y, z0, z1) -> cq.Workplane:
    return cq.Workplane("XY").circle(r).extrude(z1 - z0).translate((x, y, z0))


def csk_cutter(p, x, y, z, depth=1.4):
    """Countersink for an M2.5 flat head, widest at z, narrowing upwards."""
    return (
        cq.Workplane("XY")
        .circle(p.m25_csk_d / 2 + 0.2)
        .workplane(offset=depth)
        .circle(p.m25_clear / 2)
        .loft()
        .translate((x, y, z - 0.01))
    )


def union_all(items):
    out = None
    for it in items:
        out = it if out is None else out.union(it)
    return out


# --------------------------------------------------------------------------
# shared cutters (applied to whichever part they touch)
# --------------------------------------------------------------------------


def base_screw_points(d: Design):
    # The keyboard pocket uses nearly the full width, so the front screws sit
    # in the strip ahead of it and the side screws just behind it.
    i = d.wall + 4.0
    yb = d.kb_y0 + d.p.kb_d + 2 * d.kb_clr + 4.0
    return [
        (-d.W / 2 + i + 2.5, 5.5),
        (d.W / 2 - i - 2.5, 5.5),
        (-d.W / 2 + i + 2.5, yb),
        (d.W / 2 - i - 2.5, yb),
        (20.0, d.D - i),  # rear-left corner is taken by the Pi
        (72.0, d.D - i),  # clear of the hinge-knuckle screws
    ]


def magnet_points(d: Design):
    """Lid-latch magnets: 2 at the front edge, 2 in the lid chin / rear deck."""
    return [(-30.0, 4.5), (30.0, 4.5), (-52.0, d.D - 16.0), (52.0, d.D - 16.0)]


def port_cutters(d: Design):
    p = d.p
    cuts = []
    # I/O window in the left wall for the Pi's USB + Ethernet. The Pi sits
    # port_gap in from the wall so overmoulded plugs fit.
    cuts.append(
        box(-d.W / 2 - 1, -d.W / 2 + d.wall + 1,
            d.pi_y0 + 1.0, d.pi_y1 - 1.0,
            d.pi_z0 + 1.0, d.pi_z0 + p.pi_stack_h - 1.0)
    )
    # Power bank charge/switch window, right wall at the bay
    cuts.append(
        box(d.W / 2 - d.wall - 1, d.W / 2 + 1,
            d.bay_y0 + 14, d.bay_y1 - 14,
            d.floor + 3, d.floor + p.bat_h - 3)
    )
    # 6x6 power button, right wall, rear half
    bz = d.floor + 10
    cuts.append(
        box(d.W / 2 - d.wall - 1, d.W / 2 + 1,
            d.D - 30 - p.button / 2 - 0.2, d.D - 30 + p.button / 2 + 0.2,
            bz - p.button / 2 - 0.2, bz + p.button / 2 + 0.2)
    )
    return cuts


# --------------------------------------------------------------------------
# base
# --------------------------------------------------------------------------


def base_shell(d: Design) -> cq.Workplane:
    s = (
        cq.Workplane("XY")
        .box(d.W, d.D, d.H, centered=(True, False, False))
        .edges("|Z")
        .fillet(d.fillet_r)
    )
    return s


def build_base(d: Design):
    p = d.p
    W, D, H, Hs = d.W, d.D, d.H, d.Hs
    shell = base_shell(d)

    # ---------- base_bottom: z 0..Hs ----------
    bottom = shell.intersect(box(-W, W, -1, D + 1, 0, Hs))
    inner = box(-W / 2 + d.wall, W / 2 - d.wall, d.wall, D - d.wall, d.floor, Hs + 1)
    bottom = bottom.cut(inner)

    # divider between battery bay and electronics bay (with cable notch)
    div = box(-W / 2 + d.wall, W / 2 - d.wall, d.bay_y1, d.bay_y1 + 1.6, 0, Hs - 0.2)
    div = div.cut(box(-20, 20, d.bay_y1 - 1, d.bay_y1 + 3, d.floor + 6, Hs))
    bottom = bottom.union(div)

    # screw columns: deep counterbore from the underside, 3.5 mm of column left
    # at the top so an M2.5x8 countersunk screw reaches the insert in base_top
    col_top = 3.5
    for x, y in base_screw_points(d):
        bottom = bottom.union(zcyl(4.0, x, y, 0, Hs))
    for x, y in base_screw_points(d):
        bottom = bottom.cut(zcyl(p.m25_clear / 2, x, y, -1, Hs + 1))
        bottom = bottom.cut(zcyl(p.m25_csk_d / 2 + 0.4, x, y, -1, Hs - col_top))
        bottom = bottom.cut(csk_cutter(p, x, y, Hs - col_top))

    # Pi/HAT standoffs (heat-set inserts). The Pi is turned so USB/Ethernet
    # face -X; holes are 3.5 from the far short edge and 58 apart.
    far_edge = d.pi_x0 + p.pi_overhang + p.pi_board_w
    hx0 = far_edge - p.pi_hole_inset
    hy0 = d.pi_y1 - p.pi_hole_inset
    pi_holes = [
        (hx0, hy0),
        (hx0 - p.pi_hole_dx, hy0),
        (hx0, hy0 - p.pi_hole_dy),
        (hx0 - p.pi_hole_dx, hy0 - p.pi_hole_dy),
    ]
    for x, y in pi_holes:
        bottom = bottom.union(zcyl(3.0, x, y, 0, d.standoff_top))
    for x, y in pi_holes:
        bottom = bottom.cut(zcyl(p.insert_d / 2, x, y, d.standoff_top - p.insert_l, d.standoff_top + 1))

    # floor vents under the Pi
    for i in range(7):
        x = d.pi_x0 + 12 + i * 9
        bottom = bottom.cut(
            box(x, x + 4, d.pi_y0 + 10, d.pi_y1 - 10, -1, d.floor + 1)
        )

    # battery bay: low retaining ribs at the bay ends
    for sx in (-1, 1):
        x = sx * (p.bat_w / 2 + 0.6)
        xa, xb = (x, x + 1.6) if sx > 0 else (x - 1.6, x)
        rib = box(xa, xb, d.bay_y0 + 15, d.bay_y1 - 15, 0, d.floor + 6)
        bottom = bottom.union(rib)

    # ---------- base_top: z Hs..H ----------
    top = shell.intersect(box(-W, W, -1, D + 1, Hs, H))
    kb_pw, kb_pd = p.kb_w + d.kb_clr * 2, p.kb_d + d.kb_clr * 2
    kx0, kx1 = -kb_pw / 2, kb_pw / 2
    ky0, ky1 = d.kb_y0, d.kb_y0 + kb_pd

    hollow = box(-W / 2 + d.wall, W / 2 - d.wall, d.wall, D - d.wall, Hs - 1, H - d.deck)
    tub = box(kx0 - 2, kx1 + 2, ky0 - 2, ky1 + 2, Hs - 1, H)
    top = top.cut(hollow.cut(tub))
    # keyboard pocket
    top = top.cut(box(kx0, kx1, ky0, ky1, Hs + d.kb_floor_t, H + 1))
    # finger notches at both pocket ends
    for sx in (-1, 1):
        top = top.cut(zcyl(9, sx * kb_pw / 2, (ky0 + ky1) / 2, Hs + d.kb_floor_t + 4, H + 1))

    # insert bosses hanging from the deck
    for x, y in base_screw_points(d):
        top = top.union(zcyl(3.2, x, y, Hs, H - d.deck))
    for x, y in base_screw_points(d):
        top = top.cut(zcyl(p.insert_d / 2, x, y, Hs - 1, Hs + p.insert_l))

    # 4010 fan grill + M3 holes in the deck, right-rear bay (there is only
    # ~4 mm above the 26.1 mm Pi stack, so the fan can't sit over the Pi)
    fx = d.W / 2 - d.wall - 30.0
    fy = d.pi_y0 + 30.0
    for r in range(4, 20, 5):
        ring = zcyl(r + 2.0, fx, fy, H - d.deck - 1, H + 1).cut(
            zcyl(r, fx, fy, H - d.deck - 2, H + 2)
        )
        top = top.cut(ring)
    # keep 4 spokes
    for a in (0, 90):
        spoke = box(fx - 1.2, fx + 1.2, fy - 24, fy + 24, H - d.deck - 1, H).rotate(
            (fx, fy, 0), (fx, fy, 1), a + 45
        )
        top = top.union(spoke.intersect(zcyl(22.5, fx, fy, H - d.deck, H)))
    hp = p.fan_hole_pitch / 2
    for sx in (-1, 1):
        for sy in (-1, 1):
            top = top.cut(zcyl(p.m3_clear / 2 - 0.3, fx + sx * hp, fy + sy * hp, H - d.deck - 1, H + 1))

    # passive vent slots over the Pi
    for i in range(6):
        x = d.pi_x0 + 20 + i * 9
        top = top.cut(box(x, x + 3.5, d.pi_y0 + 8, d.pi_y1 - 12, H - d.deck - 1, H + 1))

    # magnet pockets (lid latch): short bosses under the deck
    for mx, my in magnet_points(d):
        top = top.union(zcyl(3.5, mx, my, H - d.deck - 2.0, H - d.deck + 0.01))
        top = top.cut(zcyl(p.magnet_d / 2 + 0.1, mx, my, H - p.magnet_t - 0.2, H + 1))

    # hinge: base knuckles ("D" shape: half round on a block). They are
    # separate parts bolted down through the deck, so base_top can print
    # deck-face-down with no supports and the knuckles print on their side.
    base_k, _ = d.knuckle_ranges()
    ay, az, R = d.axis_y, d.axis_z, d.R
    knuckles = {}
    for x0, x1 in base_k:
        k = xcyl(R, x0, x1, ay, az).union(box(x0, x1, ay - R, D, H, az))
        k = k.intersect(box(x0, x1, ay - R, D, H, az + R + 1))
        k = k.cut(xcyl(p.m3_tight / 2, x0 - 1, x1 + 1, ay, az))
        xc = (x0 + x1) / 2
        side = "R" if xc > 0 else "L"
        kind = "outer" if abs(xc) > d.W / 2 - d.knuckle_base_l else "inner"
        for ky in (ay - R / 2, ay + R / 2 - 0.5):
            k = k.cut(zcyl(p.insert_d / 2, xc, ky, H - 1, H + p.insert_l + 1.5))
            top = top.cut(zcyl(p.m25_clear / 2, xc, ky, H - d.deck - 1, H + 1))
            top = top.union(zcyl(3.2, xc, ky, H - d.deck - 1.5, H - d.deck + 0.01)).cut(
                zcyl(p.m25_clear / 2, xc, ky, H - d.deck - 2, H + 1))
            top = top.cut(csk_cutter(p, xc, ky, H - d.deck - 1.5))
        knuckles[f"knuckle_{side}_{kind}"] = k

    # cable slot through the deck between the knuckle groups
    cx = d.cable_x
    top = top.cut(box(cx - d.cable_w / 2, cx + d.cable_w / 2, ay - d.cable_slot / 2 - 2, ay + d.cable_slot / 2, H - d.deck - 1, H + 1))

    # pin: M3 bolt enters the outer knuckle (clearance + head recess) and is
    # held by a nut trapped in the inner face of the inner knuckle.
    for s in (1, -1):
        side = "R" if s > 0 else "L"
        outer = s * W / 2
        # 3 mm deep recess so an M3x30 socket-head sits flush and its tip ends
        # exactly at the inner face of the nut (no stub poking into the lid)
        hx0 = outer - 3.0 if s > 0 else outer - 0.01
        ko = knuckles[f"knuckle_{side}_outer"]
        ko = ko.cut(xcyl(p.m3_clear / 2, min(outer, outer - s * d.knuckle_base_l) - 1,
                         max(outer, outer - s * d.knuckle_base_l) + 1, ay, az))
        knuckles[f"knuckle_{side}_outer"] = ko.cut(xcyl(3.0, hx0, hx0 + 3.01, ay, az))
        inner_face = s * (W / 2 - 2 * d.knuckle_base_l - 2 * d.knuckle_gap - d.knuckle_lid_l)
        nx0 = inner_face if s > 0 else inner_face - p.m3_nut_t
        nut = (
            cq.Workplane("YZ")
            .polygon(6, p.m3_nut_af / math.cos(math.pi / 6))
            .extrude(p.m3_nut_t)
            .translate((nx0, ay, az))
        )
        knuckles[f"knuckle_{side}_inner"] = knuckles[f"knuckle_{side}_inner"].cut(nut)

    for c in port_cutters(d):
        bottom = bottom.cut(c)
        top = top.cut(c)

    return bottom, top, knuckles


# --------------------------------------------------------------------------
# lid (modelled closed, sitting on the base)
# --------------------------------------------------------------------------


def build_lid(d: Design):
    p = d.p
    W, D, H, Tl, R = d.W, d.D, d.H, d.Tl, d.R
    ay, az = d.axis_y, d.axis_z

    slab = (
        cq.Workplane("XY")
        .box(W, ay, Tl, centered=(True, False, False))
        .edges("|Z and <Y")
        .fillet(d.fillet_r)
        .translate((0, 0, H))
    )
    lid = slab.union(xcyl(R, -W / 2, W / 2, ay, az))

    base_k, lid_k = d.knuckle_ranges()
    # clear the base knuckles (+ swing clearance)
    for x0, x1 in base_k:
        lid = lid.cut(box(x0 - d.knuckle_gap, x1 + d.knuckle_gap, ay - R - 0.6, D + 1, H - 1, H + Tl + 1))
    # pin bores through lid knuckles (clearance fit)
    for x0, x1 in lid_k:
        lid = lid.cut(xcyl(p.m3_clear / 2, x0 - 1, x1 + 1, ay, az))

    # display position (closed: screen faces down)
    dx0 = -p.disp_w / 2
    dy0 = d.disp_front_margin
    dcx, dcy = 0.0, dy0 + p.disp_h / 2
    zb = H + d.bezel_t  # top of bezel = display front face

    # ---------- bezel: z H .. H+bezel_t ----------
    bezel = lid.intersect(box(-W, W, -1, D + 1, H - 1, zb))
    win = box(
        dcx + p.active_dx - p.active_w / 2 - 0.5,
        dcx + p.active_dx + p.active_w / 2 + 0.5,
        dcy + p.active_dy - p.active_h / 2 - 0.5,
        dcy + p.active_dy + p.active_h / 2 + 0.5,
        H - 1, zb + 1,
    )
    bezel = bezel.cut(win)

    # ---------- back: z H+bezel_t .. H+Tl ----------
    back = lid.intersect(box(-W, W, -1, D + 1, zb, H + Tl + 1))
    cavity = box(-W / 2 + d.wall, W / 2 - d.wall, d.wall, ay - 3, zb - 1, H + Tl - d.back_t)
    back = back.cut(cavity)

    # display locators: L-corners around the module outline
    t, L = 1.6, 10.0
    dx1 = dx0 + p.disp_w + d.clr
    dxa = dx0 - d.clr
    dy1 = dy0 + p.disp_h + d.clr
    dya = dy0 - d.clr
    for cx, sx in ((dxa, 1), (dx1, -1)):
        for cy, sy in ((dya, 1), (dy1, -1)):
            xa = cx - t if sx > 0 else cx
            ya = cy - t if sy > 0 else cy
            a = box(xa, xa + t, min(ya, ya + sy * L), max(ya, ya + sy * L) + t, zb, H + Tl - d.back_t + 0.01)
            b = box(min(xa, xa + sx * L), max(xa, xa + sx * L) + t, ya, ya + t, zb, H + Tl - d.back_t + 0.01)
            back = back.union(a).union(b)
    # pads that press the module against the bezel
    pad_z0 = zb + p.disp_t + 0.3
    for x in (-55, 55):
        for y in (dy0 + 15, dy0 + p.disp_h - 15):
            back = back.union(box(x - 6, x + 6, y - 6, y + 6, pad_z0, H + Tl - d.back_t + 0.01))

    # bezel screws: inserts in back bosses, M2.5 countersunk through bezel
    i = d.wall + 3.0
    # front corners, mid sides (outside the screen), and two in the chin
    # between the screen and the hinge (clear of the cable opening and magnets)
    chin_y = (dy1 + ay - 3) / 2
    lid_screws = [(-W / 2 + i, 4.6), (W / 2 - i, 4.6), (-W / 2 + i, dcy), (W / 2 - i, dcy),
                  (-40.0, chin_y), (40.0, chin_y)]
    for x, y in lid_screws:
        back = back.union(zcyl(3.0, x, y, zb, H + Tl - d.back_t + 0.01))
    for x, y in lid_screws:
        back = back.cut(zcyl(p.insert_d / 2, x, y, zb - 1, zb + p.insert_l))
        bezel = bezel.cut(zcyl(p.m25_clear / 2, x, y, H - 1, zb + 1))
        csk = (
            cq.Workplane("XY")
            .circle(p.m25_csk_d / 2 + 0.2)
            .workplane(offset=1.4)
            .circle(p.m25_clear / 2)
            .loft()
            .translate((x, y, H - 0.01))
        )
        bezel = bezel.cut(csk)

    # display mounting holes (4x d3.3 in the module frame): M2.5 countersunk
    # through the bezel, nut on the back of the module's frame
    for sx in (-1, 1):
        for sy in (-1, 1):
            hx, hy = dcx + sx * p.disp_hole_dx / 2, dcy + sy * p.disp_hole_dy / 2
            bezel = bezel.cut(zcyl(p.m25_clear / 2, hx, hy, H - 1, zb + 1))
            bezel = bezel.cut(csk_cutter(p, hx, hy, H))

    # magnets in the bezel face matching the base (boss on the inside so the
    # 2.2 mm pocket stays blind in a 2 mm bezel)
    for mx, my in magnet_points(d):
        bezel = bezel.union(zcyl(3.2, mx, my, zb - 0.01, zb + 1.0))
        bezel = bezel.cut(zcyl(p.magnet_d / 2 + 0.1, mx, my, H - 1, H + p.magnet_t + 0.2))

    # cable channel: open the rounded rear between the knuckle groups
    cw, cx = d.cable_w, d.cable_x
    back = back.cut(box(cx - cw / 2, cx + cw / 2, ay - 8, D + 1, zb - 1, H + Tl - d.back_t))
    bezel = bezel.cut(box(cx - cw / 2, cx + cw / 2, ay - d.cable_slot / 2 - 2, D + 1, H - 1, zb + 1))

    return bezel, back


# --------------------------------------------------------------------------
# reference dummies (not printed) for the assembly
# --------------------------------------------------------------------------


def build_dummies(d: Design):
    p = d.p
    kb = box(-p.kb_w / 2, p.kb_w / 2, d.kb_y0 + d.kb_clr, d.kb_y0 + d.kb_clr + p.kb_d,
             d.Hs + d.kb_floor_t, d.Hs + d.kb_floor_t + p.kb_h)
    bat = box(-p.bat_w / 2, p.bat_w / 2, d.bay_y0, d.bay_y0 + p.bat_d, d.floor, d.floor + p.bat_h)
    pi = box(d.pi_x0, d.pi_x0 + p.pi_w, d.pi_y0, d.pi_y1, d.pi_z0, d.pi_z0 + p.pi_stack_h)
    zb = d.H + d.bezel_t
    disp = box(-p.disp_w / 2, p.disp_w / 2, d.disp_front_margin, d.disp_front_margin + p.disp_h,
               zb, zb + p.disp_t)
    return {"keyboard": kb, "powerbank": bat, "pi5_stack": pi, "display": disp}


def rotate_lid(d: Design, shape: cq.Workplane, angle_deg: float) -> cq.Workplane:
    """Open the lid by angle_deg (0 = closed) about the hinge axis."""
    return shape.rotate((0, d.axis_y, d.axis_z), (1, d.axis_y, d.axis_z), -angle_deg)


# --------------------------------------------------------------------------
# export
# --------------------------------------------------------------------------


COLORS = {
    "base_bottom": (0.20, 0.22, 0.25),
    "base_top": (0.30, 0.32, 0.36),
    "lid_back": (0.30, 0.32, 0.36),
    "lid_bezel": (0.12, 0.12, 0.14),
    "keyboard": (0.85, 0.85, 0.85),
    "powerbank": (0.15, 0.45, 0.80),
    "pi5_stack": (0.10, 0.60, 0.25),
    "display": (0.05, 0.05, 0.08),
}


def build_all(d: Design):
    bottom, top, knuckles = build_base(d)
    bezel, back = build_lid(d)
    parts = {"base_bottom": bottom, "base_top": top, **knuckles, "lid_bezel": bezel, "lid_back": back}
    return parts, build_dummies(d)


def assembly(d: Design, parts, dummies, angle: float) -> cq.Assembly:
    asm = cq.Assembly(name=f"foldable_pideck_{int(angle)}deg")
    lid_names = {"lid_bezel", "lid_back", "display"}
    for name, shp in {**parts, **dummies}.items():
        s = rotate_lid(d, shp, angle) if name in lid_names else shp
        col = COLORS.get(name, COLORS["base_top"] if name.startswith("knuckle") else (0.5, 0.5, 0.5))
        asm.add(s, name=name, color=cq.Color(*col))
    return asm


def print_orientation(d: Design, name: str, shp: cq.Workplane) -> cq.Workplane:
    """Flip parts so they print flat side down without supports."""
    bb = shp.val().BoundingBox()
    if name == "base_top":
        shp = shp.rotate((0, 0, 0), (1, 0, 0), 180)  # deck face down
    elif name == "lid_back":
        shp = shp.rotate((0, 0, 0), (1, 0, 0), 180)  # back plate face down
    elif name.startswith("knuckle"):
        shp = shp.rotate((0, 0, 0), (0, 1, 0), 90)  # on its flat side, bore vertical
    bb = shp.val().BoundingBox()
    return shp.translate((-bb.center.x, -bb.center.y, -bb.zmin))


def file_name(name: str) -> str:
    """Repo naming: lowercase, hyphen-separated (knuckle_L_outer -> hinge-knuckle-left-outer)."""
    n = name.replace("_L_", "_left_").replace("_R_", "_right_")
    if n.startswith("knuckle"):
        n = "hinge_" + n
    return n.replace("_", "-").lower()


def export(d: Design, root: str, open_angle: float = 110.0):
    step_dir = os.path.join(root, "cad", "step")
    stl_dir = os.path.join(root, "stl")
    os.makedirs(step_dir, exist_ok=True)
    os.makedirs(stl_dir, exist_ok=True)
    parts, dummies = build_all(d)
    for name, shp in parts.items():
        fn = file_name(name)
        cq.exporters.export(shp, os.path.join(step_dir, f"{fn}.step"))
        cq.exporters.export(
            print_orientation(d, name, shp),
            os.path.join(stl_dir, f"{fn}.stl"),
            tolerance=0.05,
            angularTolerance=0.15,
        )
    for ang, tag in ((0, "closed"), (open_angle, "open")):
        assembly(d, parts, dummies, ang).save(os.path.join(step_dir, f"foldable-assembly-{tag}.step"))
    return parts, dummies


def summary(d: Design) -> str:
    return (
        f"Footprint {d.W:.1f} x {d.D:.1f} mm | base H {d.H:.1f} | lid T {d.Tl:.1f} | "
        f"closed {d.H + d.Tl:.1f} mm | hinge axis y={d.axis_y:.1f} z={d.axis_z:.1f}"
    )


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--angle", type=float, default=110.0, help="open angle for assembly_open.step")
    ap.add_argument("--out", default=os.path.join(os.path.dirname(__file__), "..", ".."),
                    help="repo root (writes cad/step/ and stl/)")
    a = ap.parse_args()
    d = Design()
    print(summary(d))
    export(d, os.path.abspath(a.out), a.angle)
    print("exported to", os.path.abspath(a.out))
