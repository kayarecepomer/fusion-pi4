# Exporting work from Fusion into this repo

Fusion keeps designs in the Autodesk cloud, so nothing lands in this repo until
you export it. Each design should be committed in three forms.

## 1. Native archive (`cad/fusion/`)

1. Open the design in Fusion.
2. *File > Export*.
3. Type: **Fusion Archive Files (\*.f3d)**. If the design references other
   designs (linked components), choose **Fusion Archive Files (\*.f3z)** so
   the references are bundled.
4. Save as `cad/fusion/<part-name>.f3d`.

This is the file to open when you want to keep editing with full history,
sketches and parameters.

## 2. STEP (`cad/step/`)

1. *File > Export*, type **STEP Files (\*.step)**.
2. Save as `cad/step/<part-name>.step`.

STEP keeps exact solid geometry and opens in any CAD tool, but loses the
timeline and parameters.

## 3. Print meshes (`stl/`)

1. In the browser tree, right-click each body you will print, then
   *Save As Mesh* (or *File > 3D Print* with "Send to 3D print utility" off).
2. Format **STL (Binary)** or **3MF**, refinement **High**, units **mm**.
3. Save one file per printed part, e.g. `stl/lid.stl`, `stl/base.stl`,
   `stl/hinge-left.stl`.

Export each part in the orientation you intend to print it, flat face down.

## Naming

Use lowercase, hyphen-separated names that describe the part
(`base-bottom`, `screen-bezel`, `hinge-pin`). Keep the same name across the
`.f3d`, `.step` and `.stl` versions of a part.

## Committing

```bash
git add cad stl docs
git commit -m "Add <part-name> v<n>"
git push
```

Or drag the files into the GitHub web page for the matching folder
(*Add file > Upload files*). Files over 100 MB need Git LFS; Fusion parts
are normally far smaller.
