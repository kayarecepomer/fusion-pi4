# Components: PiDeck parts reused in the foldable remix

Source build: [PiDeck – 7 Inch Cyberdeck with Raspberry Pi 5](https://makerworld.com/en/models/2619704-pideck-7-inch-cyberdeck-with-raspberry-pi-5) by Screase3D (V1, CC BY-NC-SA 4.0).
A newer [PiDeck V2](https://makerworld.com/en/models/3002561-pideck-v2-7-inch-cyberdeck-with-raspberry-pi-5) exists; differences are noted below.
The original STEP assembly and STLs are in [`reference/pideck-v1/`](../reference/pideck-v1/).

Goal of this repo: keep the same parts (keyboard, screen, Pi, screws, inserts) but repackage them as a small
clamshell laptop: a **lid** holding the screen and a **base** holding keyboard, Pi and power, joined by a hinge.

Source column: **STEP** = measured from PiDeck's own assembly (`Pi_Deck_RaspberryPi5.step`, the models the case was
designed around), **STL** = measured from the printed parts, **DS** = manufacturer datasheet/product page,
**PD** = PiDeck listing text, **TBM** = still to be measured on the real part.

## 1. Bill of materials

### Electronics

| # | Part | Qty | Exact item used by PiDeck | Key dimensions (mm) | Src |
|---|------|-----|---------------------------|---------------------|-----|
| E1 | Raspberry Pi 5 | 1 | Raspberry Pi 5 (any RAM) | PCB 85 × 56; Ø2.7 holes on **58 × 49** pattern, 3.5 from edges. Envelope with connector overhang 90.1 × 57.7 | DS + STEP |
| E2 | 7" IPS touch display | 1 | "IPS Touch LCD with cables" ([AliExpress](https://de.aliexpress.com/item/1005007432461342.html)), HDMI video + USB touch | Envelope **166.0 × 124.2 × 14.1** (incl. driver board). Glass/window pocket in frame **165.8 × 100.8**. 4 × Ø3.3 holes on **157.0 × 114.9** pattern, 4.0 / 4.6 from the outline edges | STEP + STL |
| E3 | Waveshare NVMe HAT | 1 | "Waveshare NVME hat" ([AliExpress](https://de.aliexpress.com/item/1005009817065082.html)), PCIe FFC → M.2 2280 | Board 88.0 × 56.5 × 1.6; SSD 80 × 22 × 3.5. **Pi + HAT stack 90.1 × 57.9 × 26.1** on 17.5 mm standoffs | STEP |
| E4 | Waveshare IO board (**dropped in the remix**, kaya 2026-10-05: short cables instead, saves ~30 mm base depth) | 0 | "Waveshare IO Board" ([AliExpress](https://de.aliexpress.com/item/1005010391360168.html)): 2 × full HDMI, USB-C, power header, fed by micro-HDMI/USB-C plugs into the Pi | PCB 85.0 × 33.6 × 1.0; envelope with plugs 89.0 × 39.2 × 18.8. 4 × Ø3.2 holes on **58.0 × 27.5** pattern | STEP |
| E5 | Keyboard | 1 | **Rii X1 mini wireless keyboard (rounded-edge version)**, 2.4 GHz USB dongle, built-in touchpad, 300 mAh Li-po | Model envelope **179.4 × 64.9 × 13.9**; key-field opening in frame **150.5 × 58.5** (Riitek lists 150 × 60 × 10 for the key body) | STEP + STL + DS |
| E6 | Power bank (V1) | 1 | **Anker PowerCore III Wireless 10K** (A1617 / "Anker 533"), 10 000 mAh, 18 W USB-C out | Model **152.0 × 69.0 × 19.5**; Anker lists 149 × 68 × 19, ~240 g | STEP + DS |
| E6b | PD trigger module (V2 instead of E6) | 1 | Geekworm PD module ([AliExpress](https://de.aliexpress.com/item/1005009922081522.html)), runs from a USB-C PD charger | **TBM** | PD |
| E7 | Power push button | 1 | 6 × 6 × 4.3 mm micro push button + wires ([AliExpress](https://de.aliexpress.com/item/1005002550688671.html)), wired to the Pi 5 power-button pads | 6 × 6 × 4.3 | PD |
| E8 | Fan (optional) | 1 | 4010 5 V fan (Orion OD4010) | 40 × 40 × 10 (43.4 × 43.4 × 12 with frame in model), M3 holes on 32 pitch | STEP + DS |
| E9 | Camera (V2 only, optional) | 1 | Raspberry Pi Camera 1.3 ([AliExpress](https://de.aliexpress.com/item/32988983058.html)) | 25 × 24 board | DS |

### Mechanical hardware

| # | Part | Qty (V1) | Qty (V2) | Notes | Src |
|---|------|----------|----------|-------|-----|
| H1 | M2.5 × 6 mm countersunk screw | ~17 | 17 | Main case screw ([600 pc kit](https://de.aliexpress.com/item/1005007021342718.html)) | PD |
| H2 | M2.5 × 8 mm countersunk screw | 2 | 2 | | PD |
| H3 | M2.5 × 5 mm countersunk screw | 4 | – | Pi stack to standoffs, in the STEP | STEP |
| H4 | M2 × 8 mm screw | – | 2 | | PD |
| H5 | M3 × 16 mm screw + nut | 4 | 4 | Fan mount | PD |
| H6 | M2.5 heat-set insert, Ø3.5 × 4 mm | ~27 | 27 | [AliExpress](https://de.aliexpress.com/item/1005008318533389.html). PiDeck's insert bores measure Ø3.5–3.9 in the STLs | PD + STL |
| H7 | M2.5 standoff | 4 | 6 | V1 model: 4 × 17.5 mm (Würth 970060244 style) between Pi and HAT; V2 lists 16 mm brass | STEP + PD |
| H8 | Neodymium magnet 5 × 2 mm | 8 | 4 | Magnetic flaps (SD card, power bank / rear I/O). Pocket at Ø5.2 × 2.1 | PD |

V1 screw/insert counts are not stated on the listing; the V2 counts are the best estimate.

### Print data (PiDeck V1 / V2)

| | V1 | V2 |
|---|---|---|
| Material | PLA, ~439 g | PLA, ~500 g |
| Plates / time | 7 plates, ~17.5 h | 6 plates, ~15.4 h |
| Settings | 0.2 mm layers, 3 walls, 15 % infill | same family |

## 2. How PiDeck V1 is laid out (from the STEP)

PiDeck is an upright slab: display on top, keyboard directly below it in the same front frame, and the Pi stack,
IO board, fan and power bank behind them.

| Item | Size (mm) |
|------|-----------|
| Whole deck incl. stand | 226.6 × 213.7 × 103.0 |
| Front frame (display + keyboard) | 184.0 × 201.3 × 19.3 |
| All hardware together | 179.4 × 188.8 × 56.3 deep |
| Battery housing | 170.2 × 81.0 × 32.0 |
| Back cover (fan version) | 168.4 × 124.9 × 17.5 |

## 3. What this means for the foldable layout

| Half | Contents | Footprint driver | Thickness driver |
|------|----------|------------------|------------------|
| Lid | Display (E2) | 166.0 × 124.2 envelope | 14.1 envelope; with 2 mm back wall and bezel ≈ 17–18 |
| Base | Keyboard (E5) + Pi stack (E1, E3) + power (E6 or E6b) | Keyboard 179.4 is the widest part; power bank 152.0 | Pi + HAT stack 26.1, power bank 19.5, keyboard 13.9 |

Observations:

- **The keyboard sets the width.** At 179.4 mm it is wider than the display (166.0), so both halves come out at
  roughly **185 × 130 mm** with 2–3 mm walls. PiDeck's own front frame is already 184 mm wide.
- **Base depth:** keyboard (64.9) next to the Pi stack (57.9 deep) is ~123 mm, which fits the ~130 mm the lid needs.
  The power bank (69.0) does not fit beside both, so it has to go under the keyboard, which makes the base ~37 mm (13.9 + 19.5 + walls)
  thick, or be swapped for the V2 Geekworm PD module.
- **Lowest-profile base:** Pi stack laid flat beside the keyboard, no internal power bank → about 30 mm thick,
  set by the 26.1 mm Pi + NVMe stack. Dropping the 4010 fan above the Pi or moving it to the side keeps it there.
- **Hinge cabling:** the display needs HDMI from the IO board and USB for touch and power. Use a flat FPC HDMI
  cable through a hollow hinge or a cable slot on the hinge axis.
- **Display mounting:** the four Ø3.3 holes at 157.0 × 114.9 suit M3 or M2.5 screws into heat-set inserts in the lid back.
- **No IO board:** the remix drops the Waveshare IO board. A short micro-HDMI to HDMI (or FPC HDMI) cable goes from the Pi to the display through the hinge, and the Pi's own USB/Ethernet ports face a base side wall.

## 4. Still to measure

1. Geekworm PD module outline and holes (only if going the V2 power route).
2. Display active area and the exact position of the driver board on its back (the STEP model is one solid).
3. Rii X1 rounded-edge version: confirm the 179.4 mm model width against the real keyboard with calipers.

## Sources

- [PiDeck V1 on MakerWorld](https://makerworld.com/en/models/2619704-pideck-7-inch-cyberdeck-with-raspberry-pi-5) and its STEP/STL files (in `reference/pideck-v1/`)
- [PiDeck V2 on MakerWorld](https://makerworld.com/en/models/3002561-pideck-v2-7-inch-cyberdeck-with-raspberry-pi-5)
- [Raspberry Pi 5 mechanical drawing](https://datasheets.raspberrypi.com/rpi5/raspberry-pi-5-mechanical-drawing.pdf)
- [Rii K01X1 mini keyboard spec (Riitek)](https://www.riimall.com/products/rii-k01x1-mini-wireless-keyboard)
- [Anker 533 / PowerCore III 10K Wireless (A1617)](https://www.anker.com/eu-en/products/a1617)
