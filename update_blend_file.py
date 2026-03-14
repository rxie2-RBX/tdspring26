"""Update Blender file to rename Geometry Nodes modifiers to RadianceField."""

import bpy
from pathlib import Path

def update_modifiers_in_blend(blend_file: Path) -> None:
    """Open a blend file and rename all 'Geometry Nodes' modifiers to 'RadianceField'."""
    
    # Open the blend file
    bpy.ops.wm.open_mainfile(filepath=str(blend_file))
    print(f"[+] Opened: {blend_file}")
    
    # Iterate through all objects in the scene
    updated_count = 0
    for obj in bpy.data.objects:
        print(f"    Checking object: {obj.name}")
        
        # Check all modifiers
        for modifier in obj.modifiers:
            print(f"      Modifier: {modifier.name} (type: {modifier.type})")
            
            # If it's a NODES type modifier with a generic name, rename it to RadianceField
            if modifier.type == "NODES":
                if modifier.name != "RadianceField":
                    old_name = modifier.name
                    modifier.name = "RadianceField"
                    print(f"        [+] Renamed: {old_name} -> RadianceField")
                    updated_count += 1
                else:
                    print(f"        [+] Already named: RadianceField")
    
    print(f"\n[+] Total modifiers updated: {updated_count}")
    
    # Save the file
    bpy.ops.wm.save_mainfile(filepath=str(blend_file))
    print(f"[+] Saved: {blend_file}")

if __name__ == "__main__":
    blend_file = Path.cwd() / "combined_michelle_hydrant.blend"
    
    if not blend_file.exists():
        print(f"Error: File not found: {blend_file}")
        exit(1)
    
    print(f"Updating: {blend_file}")
    print("=" * 50)
    
    update_modifiers_in_blend(blend_file)
    
    print("=" * 50)
    print("[*] Done!")
