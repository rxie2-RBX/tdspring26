# Task 3: Pointcloud Bounding Box Parameters

## Backlog Requirement
The bounding box for the pointcloud should be set in `bpy.data.objects["Pointcloud"].modifiers["RadianceField"]["Socket_3"][0|1|2]`

## Implementation Status
✅ **COMPLETED**

## Key Functions
- `set_radiancefield_input()` (line 352) - Set individual socket values on RadianceField modifier
- `set_pointcloud_bounding_box()` (line 386) - Convenience wrapper for setting bounding box

## Features
- Sets bounding box parameters on RadianceField (Socket_3)
- Attempts primary socket format: `geo_mod["Socket_3"] = (x, y, z)`
- Falls back to alternative naming schemes if primary fails
- Integrates with radiancefield modifier from Task 2

## CLI Integration
The `create()` command supports:
- `--bbox-x` - Bounding box X parameter
- `--bbox-y` - Bounding box Y parameter
- `--bbox-z` - Bounding box Z parameter

Only applied when:
1. Pointclouds were imported
2. RadianceField was loaded
3. At least one bbox parameter is non-zero

## Example Usage
```bash
python project2_ex1_fbx_tiktok.py create character.fbx \
    --pointcloud cloud.ply \
    --bbox-x 1.0 \
    --bbox-y 1.0 \
    --bbox-z 1.0
```

## Code Location
- Input setter: line 352-384
- Bounding box setter: line 386-420
- CLI integration: `create()` function lines 909-916
