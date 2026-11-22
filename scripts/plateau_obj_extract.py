#!/usr/bin/env python3
"""Extract a real, identifiable PLATEAU OBJ tower mesh (never synthesize one).

Usage:
  python -m pip install numpy trimesh pyproj
  python scripts/plateau_obj_extract.py --obj FILE.obj --landmark tower --output OUTPUT.json
"""
import argparse
import json
from pathlib import Path
import numpy as np
import trimesh
from pyproj import Transformer

LOC = {
    "tower": (139.74543, 35.65858, 333),
    "skytree": (139.81070, 35.71006, 634),
}


def extract(obj: Path, landmark: str, radius: float) -> dict:
    lon, lat, known_height = LOC[landmark]
    x, y = Transformer.from_crs("EPSG:4326", "EPSG:6677", always_xy=True).transform(lon,lat)
    scene = trimesh.load(str(obj), force="scene", process=False)
    candidates = []
    for mesh in scene.geometry.values():
        if not isinstance(mesh, trimesh.Trimesh) or not len(mesh.faces):
            continue
        try:
            parts = mesh.split(only_watertight=False)
        except Exception:
            parts = [mesh]
        for part in parts:
            v = np.asarray(part.vertices)
            if len(v) < 3 or not np.isfinite(v).all():
                continue
            distance = np.linalg.norm(v[:, :2].mean(axis=0) - [x, y])
            span = v.max(axis=0) - v.min(axis=0)
            height = float(span[2])
            if distance < radius * 1.8 and height >= known_height * .50:
                candidates.append((height - distance * .8 - max(span[:2]) * .05, part))
    if not candidates:
        raise ValueError("No credible tower geometry at the actual PLATEAU location. Do not publish a stand-in as PLATEAU.")
    mesh = max(candidates, key=lambda pair: pair[0])[1]
    v = np.asarray(mesh.vertices, dtype=float)
    zmin = float(v[:,2].min())
    height = float(v[:,2].max() - zmin)
    if not .5 * known_height <= height <= 1.3 * known_height:
        raise ValueError(f"Invalid tower height: {height:.2f} m.")
    if len(mesh.faces) > 100000:
        raise ValueError("Mesh too dense. Simplify selected mesh using Blender before converting.")
    # Original OBJ: X=Easting, Y=Northing, Z=height (EPSG:6677).
    # App: X=Easting, Y=height, Z=-Northing.
    local = np.column_stack((v[:,0]-x, v[:,2]-zmin, -(v[:,1]-y)))
    faces = np.asarray(mesh.faces, dtype=int)
    triangles = [local[face].round(4).reshape(-1).tolist() for face in faces]
    return {
        "source":"PLATEAU", "source_file":obj.name,
        "license_note":"出典：国土交通省 Project PLATEAU 3D都市モデルを加工して作成",
        "landmark":landmark,"height_m":round(height,2),
        "triangles":triangles,"appearance":"source textures not yet baked",
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--obj", required=True, type=Path)
    ap.add_argument("--landmark", required=True, choices=LOC)
    ap.add_argument("--radius", type=float, default=75)
    ap.add_argument("--output", required=True, type=Path)
    a = ap.parse_args()
    model = extract(a.obj, a.landmark, a.radius)
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(model,ensure_ascii=False,separators=(",",":")),encoding="utf-8")
    print(f"Validated {a.landmark}: {model['height_m']} m; {len(model['triangles'])} triangles")


if __name__ == "__main__":
    main()
