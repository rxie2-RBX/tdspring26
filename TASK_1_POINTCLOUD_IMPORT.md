# Task 1: Pointcloud Import Support

## Backlog Requirement
CLI: Import a specific pointcloud file from the pointclouds/ folder, or import all pointclouds in the folder.

## Implementation Status
✅ **COMPLETED**

## Key Functions
- `import_ply()` (line 124) - Imports a single PLY file
- `get_pointcloud_files()` (line 257) - Discovers all PLY files in a folder
- `apply_material_to_object()` (line 196) - Apply material for visualization

## CLI Integration
The `create()` command supports:
- `--pointcloud` / `--ply` - Import specific PLY file
- `--pointcloud-folder` - Import all PLY files from folder

## Example Usage
```bash
# Import single pointcloud
python project2_ex1_fbx_tiktok.py create character.fbx --pointcloud cloud.ply

# Import all pointclouds from folder
python project2_ex1_fbx_tiktok.py create character.fbx --pointcloud-folder ./pointclouds/
```

## Code Location
- Implementation: `exercises/project2/project2_ex1_fbx_tiktok.py` lines 124-256
- CLI integration: `create()` function lines 870-880
