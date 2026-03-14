# Task 4: FBX Character Import with Positioning

## Backlog Requirement
After importing pointcloud(s), import either a specific character FBX file or all FBX files from a folder. Place each character at a specified location and rotation (best fit for the pointcloud) via CLI.

## Implementation Status
✅ **COMPLETED**

## Key Functions
- `get_fbx_files()` (line 432) - Discover all .fbx files in a folder
- `import_fbx()` (line 454) - Import FBX file (single file only, as specified in task)
- `find_armature()` (line 476) - Find the armature object from imported objects
- `get_target_world_location()` (line 486) - Get world location of a bone (for camera tracking)
- `position_object()` (line 444) - Set object location
- `rotate_object()` (line 270) - Set object rotation

## Features
- Imports FBX character with all associated objects (armature, mesh, materials)
- Positions character at user-specified coordinates
- Rotates character by specified angles
- Finds armature for animation tracking
- Supports bone-based world location queries

## CLI Integration
The `create()` command requires:
- `fbx_file` (argument) - Required path to FBX character file

Optional parameters:
- `--char-x`, `--char-y`, `--char-z` - Character position
- `--char-rx`, `--char-ry`, `--char-rz` - Character rotation (degrees)
- `--bone` / `-b` - Target bone for camera tracking (default: "mixamorig:Hips")

## Example Usage
```bash
python project2_ex1_fbx_tiktok.py create character.fbx \
    --pointcloud cloud.ply \
    --char-x 0.0 \
    --char-y 0.0 \
    --char-z 0.0 \
    --char-rx 0.0 \
    --char-ry 0.0 \
    --char-rz 0.0
```

## Code Location
- FBX file discovery: line 432-442
- FBX import: line 454-475
- Armature finding: line 476-484
- World location query: line 486-497
- Positioning: `create()` function lines 926-938
- Rotation: `create()` function lines 941-952
