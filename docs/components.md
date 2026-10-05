# Components: PiDeck parts reused in the foldable remix

Source build: [PiDeck – 7 Inch Cyberdeck with Raspberry Pi 5](https://makerworld.com/en/models/2619704-pideck-7-inch-cyberdeck-with-raspberry-pi-5) by Screase3D (V1).
A newer [PiDeck V2](https://makerworld.com/en/models/3002561-pideck-v2-7-inch-cyberdeck-with-raspberry-pi-5) exists; differences are noted below.

Goal of this repo: keep the same parts (keyboard, screen, Pi, screws, inserts) but repackage them as a small
clamshell laptop: a **lid** holding the screen and a **base** holding keyboard, Pi and power, joined by a hinge.

Confidence column: **DS** = from a manufacturer datasheet/product page, **PD** = from the PiDeck listing,
**TBM** = to be measured on the real part with calipers before modelling.

## 1. Bill of materials

### Electronics

| # | Part | Qty | Exact item used by PiDeck | Key dimensions | Src |
|---|------|-----|---------------------------|----------------|-----|
| E1 | Raspberry Pi 5 | 1 | Raspberry Pi 5 (any RAM) | PCB 85 × 56 mm; holes Ø2.7 mm (M2.5) on a 58 × 49 mm pattern, 3.5 mm in from the edges | DS |
| E2 | 7" IPS touch display | 1 | "IPS Touch LCD with cables" ([AliExpress](https://de.aliexpress.com/item/1005007432461342.html)), HDMI video + USB touch | Typical 7" 1024×600 HDMI panels are ~165 × 100 mm outline, ~15–20 mm thick with driver board. Exact outline, bezel and hole positions **TBM** | TBM |
| E3 | Waveshare NVMe HAT | 1 | "Waveshare NVME hat" ([AliExpress](https://de.aliexpress.com/item/1005009817065082.html)), PCIe FFC to M.2 | Uses the Pi's 58 × 49 hole pattern; stack height **TBM** | PD/TBM |
| E4 | Waveshare IO board | 1 | "Waveshare IO Board" ([AliExpress](https://de.aliexpress.com/item/1005010391360168.html)), breaks Pi ports out to the case wall | **TBM** | PD/TBM |
| E5 | Keyboard | 1 | **Rii X1 mini wireless keyboard (rounded-edge version)**, 2.4 GHz USB dongle, built-in touchpad, 300 mAh Li-po | 150 × 60 × 10 mm (Riitek spec) | DS |
| E6 | Power bank (V1) | 1 | **Anker PowerCore III Wireless 10K** (A1617 / "Anker 533"), 10 000 mAh, 18 W USB-C out | 149.5 × 68.5 × 19.5 mm max (PiDeck); Anker lists 149 × 68 × 19 mm, ~240 g | DS/PD |
| E6b | PD trigger module (V2 instead of E6) | 1 | Geekworm PD module ([AliExpress](https://de.aliexpress.com/item/1005009922081522.html)), runs from a USB-C PD charger | **TBM** | PD |
| E7 | Power push button | 1 | 6 × 6 × 4.3 mm micro push button + wires ([AliExpress](https://de.aliexpress.com/item/1005002550688671.html)), wired to the Pi 5 power-button pads | 6 × 6 × 4.3 mm | PD |
| E8 | Fan (optional) | 1 | 4010 5 V fan | 40 × 40 × 10 mm, M3 holes on 32 mm pitch | DS |
| E9 | Camera (V2 only, optional) | 1 | Raspberry Pi Camera 1.3 ([AliExpress](https://de.aliexpress.com/item/32988983058.html)) | 25 × 24 mm board | DS |

### Mechanical hardware

| # | Part | Qty (V1) | Qty (V2) | Notes | Src |
|---|------|----------|----------|-------|-----|
| H1 | M2.5 × 6 mm countersunk screw | ~17 | 17 | Main case screw ([600 pc kit](https://de.aliexpress.com/item/1005007021342718.html)) | PD |
| H2 | M2.5 × 8 mm countersunk screw | 2 | 2 | | PD |
| H3 | M2 × 8 mm screw | – | 2 | | PD |
| H4 | M3 × 16 mm screw + nut | 4 | 4 | Fan mount | PD |
| H5 | M2.5 heat-set insert, Ø3.5 × 4 mm | ~27 | 27 | [AliExpress](https://de.aliexpress.com/item/1005008318533389.html). Model holes at ~Ø3.2–3.4 mm, ≥5 mm deep | PD |
| H6 | M2.5 × 16 mm brass standoff | – | 6 | Pi / HAT stack | PD |
| H7 | Neodymium magnet 5 × 2 mm | 8 | 4 | Magnetic flaps (SD card, power bank / rear I/O). Pocket at Ø5.2 × 2.1 mm | PD |

V1 qty for screws/inserts is not stated on the listing; the V2 counts are the best estimate.

### Print data (PiDeck V1 / V2)

| | V1 | V2 |
|---|---|---|
| Material | PLA, ~439 g | PLA, ~500 g |
| Plates / time | 7 plates, ~17.5 h | 6 plates, ~15.4 h |
| Settings | 0.2 mm layers, 3 walls, 15 % infill | same family |

## 2. What this means for the foldable layout

Rough envelope from the parts above (before walls and clearance):

| Half | Contents | Footprint driver | Thickness driver |
|------|----------|------------------|------------------|
| Lid | Display (E2) | ~165 × 100 mm panel | Panel + HDMI/driver board, ~15–20 mm (TBM) |
| Base | Keyboard (E5) + Pi 5 stack (E1, E3, E4) + power (E6 or E6b) | Power bank is the longest part at 149.5 mm; keyboard is 150 mm | Power bank 19.5 mm, or Pi + NVMe + fan stack ~30 mm+ |

Observations:

- The keyboard (150 mm) and the power bank (149.5 mm) are almost exactly the display width (~165 mm), so a
  ~175 × 110 mm footprint for both halves is a realistic starting point.
- The Anker power bank is the thickest single item in the base. Switching to the V2 approach (Geekworm PD module
  plus external USB-C charger) frees roughly 70 × 150 × 20 mm and makes a thin base much easier.
- The HDMI and USB-touch cables must cross the hinge. Plan a hollow hinge or a cable channel, and allow for
  the bend radius of the HDMI cable (or use a flat FPC HDMI cable).
- The Rii X1 is a stand-alone wireless keyboard; it can sit in a pocket in the base with its USB charging port
  reachable. Its touchpad side should face the user.
- The display draws power from the Pi's USB, so no extra supply wires go into the lid.

## 3. To measure before CAD

1. Display: outline, glass vs. PCB size, mounting hole positions, driver-board position and connector heights.
2. Waveshare IO board and NVMe HAT: outline, hole pattern, total stack height on the Pi.
3. Rii X1 (rounded-edge version): exact outline radius and thickness at the touchpad end.
4. Geekworm PD module (if going the V2 route): outline and holes.
5. The PiDeck STEP files (provided on MakerWorld) can be imported into Fusion to read hole and pocket positions
   directly instead of measuring.

## Sources

- [PiDeck V1 on MakerWorld](https://makerworld.com/en/models/2619704-pideck-7-inch-cyberdeck-with-raspberry-pi-5)
- [PiDeck V2 on MakerWorld](https://makerworld.com/en/models/3002561-pideck-v2-7-inch-cyberdeck-with-raspberry-pi-5)
- [Raspberry Pi 5 mechanical drawing](https://datasheets.raspberrypi.com/rpi5/raspberry-pi-5-mechanical-drawing.pdf)
- [Rii K01X1 mini keyboard spec (Riitek)](https://www.riimall.com/products/rii-k01x1-mini-wireless-keyboard)
- [Anker 533 / PowerCore III 10K Wireless (A1617)](https://www.anker.com/eu-en/products/a1617)
- [7" IPS 1024×600 HDMI touch LCD reference (The Pi Hut)](https://thepihut.com/products/7-ips-capacitive-hdmi-touch-screen-lcd-1024x600)
