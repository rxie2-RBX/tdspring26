"""Verify RadianceField modifier in the blend file."""

import bpy
from pathlib import Path

blend_file = Path.cwd() / "combined_michelle_hydrant.blend"
bpy.ops.wm.open_mainfile(filepath=str(blend_file))

print("[+] Checking modifiers in combined_michelle_hydrant.blend")
print("=" * 50)

pointcloud = bpy.data.objects.get('Pointcloud')
if pointcloud:
    print(f"[+] Found Pointcloud object")
    if pointcloud.modifiers:
        print(f"[+] Modifiers ({len(pointcloud.modifiers)}):")
        for mod in pointcloud.modifiers:
            print(f"    - {mod.name} (type: {mod.type})")
        
        # Check for RadianceField
        radiance_found = any(m.name == "RadianceField" for m in pointcloud.modifiers)
        if radiance_found:
            print(f"\n[+] ✅ RadianceField modifier found!")
        else:
            print(f"\n[!] RadianceField modifier not found")
    else:
        print(f"[!] No modifiers on Pointcloud")
else:
    print(f"[!] Pointcloud object not found")

print("=" * 50)
