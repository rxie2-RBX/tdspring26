# Task 5: Animation Rendering (PNG / MP4)

## Backlog Requirement
Render either a single frame (for testing) or the full animation. Output should be either mp4 or png, with filenames combining the pointcloud and character names (e.g., pointcloudname_charactername.mp4 or .png). We should use the tiktok animation renderer technique.

## Implementation Status
✅ **COMPLETED**

## Key Functions
- `render_frame()` (line 620) - Render a single frame to PNG
- `render_animation()` (line 638) - Render animation sequence to PNG or MP4
- `generate_output_filename()` (line 712) - Generate filename from pointcloud + character names

## Features
- **Single frame rendering**: Supports testing specific frames
- **PNG sequence output**: Renders animation frames as individual PNG files
- **MP4 output**: Converts PNG sequence to MPEG-4 video using FFmpeg
  - Bitrate: 1600 kbps (optimized for fast encoding)
  - Preset: faster (prioritizes speed)
  - FPS: 24
- **Auto frame end detection**: Uses `bpy.data.objects['Armature'].animation_data.action.frame_range[1]`
- **Smart naming**: Combines pointcloud and character file names in output filename
- **TikTok optimization**: 9:16 vertical aspect ratio (1080x1920)

## CLI Integration
The `create()` command supports:
- `--render` - Enable rendering (no arguments needed)
- `--render-frame` - Render specific frame (single frame mode)
- `--render-format` - Output format: 'png' or 'mp4' (default: 'png')
- `--render-output` / `-r` - Output directory path
- `--start` / `-s` - Animation start frame (default: 1)
- `--end` / `-e` - Animation end frame (auto-detected if omitted)

## Example Usage

### Single frame render (PNG)
```bash
python project2_ex1_fbx_tiktok.py create character.fbx \
    --pointcloud cloud.ply \
    --render \
    --render-frame 50 \
    --render-format png
```

### Full animation render (MP4)
```bash
python project2_ex1_fbx_tiktok.py create character.fbx \
    --pointcloud cloud.ply \
    --render \
    --render-format mp4 \
    --render-output ./renders/ \
    --start 1 \
    --end 184
```

### Full animation render (PNG sequence)
```bash
python project2_ex1_fbx_tiktok.py create character.fbx \
    --pointcloud cloud.ply \
    --render \
    --render-format png \
    --render-output ./renders/
```

## Output Format
- **Filename**: `{pointcloud_name}_{character_name}.{format}`
- **Example**: `Mailbox_point_cloud_doozy_hiphop.mp4`
- **PNG sequence**: `{pointcloud_name}_{character_name}_000001.png`, etc.

## Technical Details
- Uses Cycles render engine for GPU support
- PNG sequence rendered first as intermediate, then converted if MP4 requested
- Automatic cleanup of PNG files after MP4 conversion completes
- Error handling for FFmpeg availability

## Code Location
- Single frame renderer: line 620-637
- Animation renderer: line 638-710
- Filename generator: line 712-731
- CLI integration: `create()` function lines 978-1020
- Frame range determination: lines 955-961
