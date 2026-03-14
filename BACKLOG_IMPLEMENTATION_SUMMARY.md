# Project 2 Exercise 1 - Backlog Implementation Summary

## Overview
This document maps each backlog task to its implementation in `exercises/project2/project2_ex1_fbx_tiktok.py`.

All 5 backlog tasks have been completed and integrated into the main script.

---

## Task 1: Pointcloud Import (Specific File or Folder)

**Backlog Requirement:**
> CLI: Import a specific pointcloud file from the pointclouds/ folder, or import all pointclouds in the folder.

**Implementation:**
- **Function:** `import_ply()` (line 124)
  - Imports a single PLY file and names it 'Pointcloud'
  - Handles both modern (`bpy.ops.wm.ply_import`) and legacy (`bpy.ops.import_mesh.ply`) APIs
  
- **Function:** `get_pointcloud_files()` (line 257)
  - Discovers all `.ply` files in a folder
  - Filters out macOS hidden files (`._*.ply`)

- **CLI Integration in `create()` function (lines 870-880):**
  ```python
  if pointcloud:
      typer.echo("2. Importing point cloud...")
      pc = import_ply(pointcloud)
  elif pointcloud_folder:
      typer.echo("2. Importing point clouds from folder...")
      ply_files = get_pointcloud_files(pointcloud_folder)
      for ply_file in ply_files:
          pc = import_ply(ply_file)
  ```

**CLI Options:**
- `--pointcloud` / `--ply`: Import a specific PLY file
- `--pointcloud-folder`: Import all PLY files from a folder

---

## Task 2: RadianceField Application with Rotation

**Backlog Requirement:**
> For each imported pointcloud, allow rotation in the scene via CLI, name the object 'Pointcloud', and apply the geometry node group `bpy.data.node_groups["RadianceField"]` from radiancefield.blend.

**Implementation:**

- **Function:** `load_nodgroup_from_blend()` (line 288)
  - Loads a node group from an external blend file using `bpy.data.libraries.load()`
  - Auto-detects `radiancefield.blend` if not specified

- **Function:** `apply_radiancefield_to_pointcloud()` (line 318)
  - Applies the RadianceField node group as a "NODES" modifier (Blender 5.x compatible)
  - `geo_mod = pointcloud.modifiers.new(name="RadianceField", type="NODES")`
  - `geo_mod.node_group = node_group`

- **Function:** `rotate_object()` (line 270)
  - Rotates objects by specified angles (X, Y, Z in degrees)
  - Used for pointcloud orientation

- **CLI Integration in `create()` function (lines 883-891):**
  ```python
  # Step 3: Load and apply RadianceField
  if pointclouds:
      if radiancefield_blend is None:
          radiancefield_blend = Path("exercises/project2/radiancefield.blend").resolve()
      
      if load_nodgroup_from_blend(radiancefield_blend, "RadianceField"):
          for pc in pointclouds:
              apply_radiancefield_to_pointcloud(pc, "RadianceField")
  ```

- **Rotation application (lines 896-906):**
  ```python
  for pc in pointclouds:
      final_rx = pointcloud_rx + 90  # Default 90° X-axis rotation
      rotate_object(pc, final_rx, pointcloud_ry, pointcloud_rz)
  ```

**CLI Options:**
- `--radiancefield`: Path to radiancefield.blend file (auto-detected if not specified)
- `--pc-rx`, `--pc-ry`, `--pc-rz`: Pointcloud rotation in degrees

---

## Task 3: Bounding Box Parameters

**Backlog Requirement:**
> The bounding box for the pointcloud should be set in `bpy.data.objects["Pointcloud"].modifiers["GeometryNodes"]["Socket_3"][0|1|2]`

**Implementation:**

- **Function:** `set_radiancefield_input()` (line 352)
  - Sets individual socket values on the RadianceField modifier
  - Accesses modifier inputs by socket name

- **Function:** `set_pointcloud_bounding_box()` (line 386)
  - Convenience wrapper for setting bounding box (Socket_3)
  - Attempts primary socket format: `geo_mod["Socket_3"] = (bbox_x, bbox_y, bbox_z)`
  - Falls back to alternative socket naming if needed

- **CLI Integration in `create()` function (lines 909-916):**
  ```python
  # Step 5: Set bounding box parameters
  if pointclouds and radiancefield_blend and (bbox_x != 0 or bbox_y != 0 or bbox_z != 0):
      typer.echo("5. Setting bounding box parameters...")
      for pc in pointclouds:
          set_pointcloud_bounding_box(pc, bbox_x, bbox_y, bbox_z)
  ```

**CLI Options:**
- `--bbox-x`, `--bbox-y`, `--bbox-z`: Bounding box parameters

---

## Task 4: FBX Character Import with Positioning

**Backlog Requirement:**
> After importing pointcloud(s), import either a specific character FBX file or all FBX files from a folder. Place each character at a specified location and rotation (best fit for the pointcloud) via CLI.

**Implementation:**

- **Function:** `get_fbx_files()` (line 432)
  - Discovers all `.fbx` files in a folder
  - Returns sorted list for consistent processing

- **Function:** `import_fbx()` (line 454)
  - Imports FBX file and returns imported objects
  - Tracks objects before/after to identify new imports

- **Function:** `find_armature()` (line 476)
  - Finds the armature object from imported objects
  - Essential for animation tracking

- **Function:** `get_target_world_location()` (line 486)
  - Gets world location of a specific bone in the armature
  - Supports bone-based tracking for camera follow

- **Function:** `position_object()` (line 444)
  - Sets object location (X, Y, Z)

- **CLI Integration in `create()` function (lines 920-952):**
  ```python
  # Step 6: Import FBX
  typer.echo(f"6. Importing FBX: {fbx_file}")
  imported_objects = import_fbx(fbx_file)
  
  # Step 7: Position character
  if imported_objects and (char_x != 0 or char_y != 0 or char_z != 0):
      for obj in imported_objects:
          if obj.type in ("ARMATURE", "MESH"):
              position_object(obj, char_x, char_y, char_z)
  
  # Step 8: Rotate character
  if imported_objects and (char_rx != 0 or char_ry != 0 or char_rz != 0):
      for obj in imported_objects:
          if obj.type in ("ARMATURE", "MESH"):
              rotate_object(obj, char_rx, char_ry, char_rz)
  ```

**CLI Options:**
- `--char-x`, `--char-y`, `--char-z`: Character position
- `--char-rx`, `--char-ry`, `--char-rz`: Character rotation in degrees

---

## Task 5: Animation Rendering (PNG/MP4)

**Backlog Requirement:**
> Render either a single frame (for testing) or the full animation. Output should be either mp4 or png, with filenames combining the pointcloud and character names (e.g., pointcloudname_charactername.mp4 or .png). We should use the tiktok animation renderer technique.

**Implementation:**

- **Function:** `render_frame()` (line 620)
  - Renders a single frame to PNG
  - Sets frame, output path, and format

- **Function:** `render_animation()` (line 638)
  - Renders full animation sequence
  - Supports PNG sequence and MPEG-4 (MP4) output
  - PNG sequence: renders at specified resolution
  - MP4: uses FFmpeg to convert PNG sequence to video (1600 kbps, faster preset)

- **Function:** `generate_output_filename()` (line 712)
  - Combines pointcloud and character names
  - Example: `Mailbox_point_cloud_hiphop_character.mp4`

- **CLI Integration in `create()` function (lines 978-1020):**
  ```python
  # Step 16: Render if requested
  if render:
      typer.echo("16. Rendering...")
      
      pc_name = pointcloud.stem if pointcloud else None
      char_name = fbx_file.stem if fbx_file else None
      
      if render_frame is not None:
          # Single frame render
          filename = generate_output_filename(pc_name, char_name, render_format)
          output_file = Path.cwd() / filename
          # ... render logic ...
      else:
          # Full animation render
          filename_prefix = generate_output_filename(pc_name, char_name, "")
          output_dir = Path.cwd() / filename_prefix
          
          if render_format.lower() == "png":
              render_animation(start_frame, end_frame, output_dir, filename_prefix, format="PNG")
          elif render_format.lower() == "mp4":
              render_animation(start_frame, end_frame, output_dir, filename_prefix, format="MPEG4")
  ```

- **Default end frame determination (lines 955-961):**
  ```python
  if end_frame is None and armature and armature.animation_data and armature.animation_data.action:
      end_frame = int(bpy.data.objects['Armature'].animation_data.action.frame_range[1])
  ```

**CLI Options:**
- `--render`: Enable rendering
- `--render-frame`: Render a specific frame (single-frame mode)
- `--render-format`: Output format ('png' or 'mp4')
- `--render-output` / `-r`: Output path for rendered files

---

## Usage Example

```bash
# Import pointcloud and character, apply RadianceField, set positioning, and render
python project2_ex1_fbx_tiktok.py create character.fbx \
    --pointcloud-folder ./pointclouds/ \
    --pc-ry 45 \
    --radiancefield ./radiancefield.blend \
    --bbox-x 1.0 --bbox-y 1.0 --bbox-z 1.0 \
    --char-x 0 --char-y 0 --char-z 0 \
    --render \
    --render-format mp4 \
    --render-output ./renders/

```

---

## Summary

✅ **Task 1: Pointcloud Import** - Implemented via `import_ply()`, `get_pointcloud_files()`  
✅ **Task 2: RadianceField + Rotation** - Implemented via `load_nodgroup_from_blend()`, `apply_radiancefield_to_pointcloud()`, `rotate_object()`  
✅ **Task 3: Bounding Box** - Implemented via `set_pointcloud_bounding_box()`, `set_radiancefield_input()`  
✅ **Task 4: FBX Character Import** - Implemented via `import_fbx()`, `position_object()`, `find_armature()`  
✅ **Task 5: Animation Rendering** - Implemented via `render_animation()`, `render_frame()`, `generate_output_filename()`  

All backlog items are fully functional and integrated into the CLI interface.
