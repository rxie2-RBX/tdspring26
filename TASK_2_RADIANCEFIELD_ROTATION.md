# Task 2: RadianceField Application with Rotation

## Backlog Requirement
For each imported pointcloud, allow rotation in the scene via CLI, name the object 'Pointcloud', and apply the geometry node group `bpy.data.node_groups["RadianceField"]` from radiancefield.blend.

## Implementation Status
✅ **COMPLETED**

## Key Functions
- `load_nodgroup_from_blend()` (line 288) - Load RadianceField node group from external .blend file
- `apply_radiancefield_to_pointcloud()` (line 318) - Apply RadianceField as "NODES" modifier
- `rotate_object()` (line 270) - Rotate pointcloud by X, Y, Z angles

## Features
- Auto-detects `radiancefield.blend` if not specified
- Uses Blender 5.x compatible "NODES" modifier type
- Applies default 90° X-axis rotation plus user-specified rotations
- Supports custom file path via CLI option

## CLI Integration
The `create()` command supports:
- `--radiancefield` - Path to radiancefield.blend (auto-detected if omitted)
- `--pc-rx`, `--pc-ry`, `--pc-rz` - Pointcloud rotation parameters (degrees)

## Example Usage
```bash
python project2_ex1_fbx_tiktok.py create character.fbx \
    --pointcloud cloud.ply \
    --radiancefield ./radiancefield.blend \
    --pc-ry 45
```

## Code Location
- Node group loading: line 288-315
- RadianceField application: line 318-350
- Rotation logic: line 270-286
- CLI integration: `create()` function lines 883-906
