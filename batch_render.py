#!/usr/bin/env python3
"""
Batch rendering script for 15 video combinations:
- doozy-hiphop.fbx × 5 point clouds
- michelle-hiphop.fbx × 5 point clouds  
- mouse-hiphop.fbx × 5 point clouds

Each combination is rendered sequentially with MP4 output using GPU rendering.
"""

import subprocess
import sys
from pathlib import Path

# Define working directory
WORK_DIR = Path(__file__).parent
SCRIPT_PATH = WORK_DIR / "exercises" / "project2" / "project2_ex1_fbx_tiktok.py"
RADIANCEFIELD_PATH = WORK_DIR / "exercises" / "project2" / "radiancefield.blend"
CHARACTERS_DIR = WORK_DIR / "characters"
POINTCLOUDS_DIR = WORK_DIR / "pointclouds"
RENDERS_DIR = WORK_DIR / "renders"

# Character FBX files
FBX_FILES = [
    "doozy-hiphop.fbx",
    "michelle-hiphop.fbx", 
    "mouse-hiphop.fbx"
]

# Point cloud PLY files (exclude macOS hidden files)
PLY_FILES = [
    "Mailbox_point_cloud.ply",
    "Hydrant_vertical_point_cloud.ply",
    "David_Bust_point_cloud.ply",
    "McLaren_point_cloud.ply",
    "Panzernashorn_Tobler_point_cloud.ply"
]

def run_render(fbx_name: str, ply_name: str, render_num: int, total: int) -> bool:
    """Run a single render job with the given FBX and PLY files."""
    fbx_path = CHARACTERS_DIR / fbx_name
    ply_path = POINTCLOUDS_DIR / ply_name
    output_dir = RENDERS_DIR / f"{fbx_name.replace('.fbx', '')}_{ply_name.replace('.ply', '')}"
    
    if not fbx_path.exists():
        print(f"❌ FBX not found: {fbx_path}")
        return False
    
    if not ply_path.exists():
        print(f"❌ PLY not found: {ply_path}")
        return False
    
    print(f"\n{'='*70}")
    print(f"[{render_num}/{total}] Rendering: {fbx_name} + {ply_name}")
    print(f"Output: {output_dir}")
    print(f"{'='*70}\n")
    
    # Use forward slashes for cross-platform compatibility
    fbx_rel = str(fbx_path.relative_to(WORK_DIR)).replace("\\", "/")
    ply_rel = str(ply_path.relative_to(WORK_DIR)).replace("\\", "/")
    rf_rel = str(RADIANCEFIELD_PATH.relative_to(WORK_DIR)).replace("\\", "/")
    out_rel = str(output_dir.relative_to(WORK_DIR)).replace("\\", "/")
    
    # Build command using absolute paths to avoid path parsing issues
    cmd = [
        sys.executable,
        str(SCRIPT_PATH),
        str(fbx_path),  # Use absolute path for positional argument
        "--pointcloud", str(ply_path),
        "--radiancefield", str(RADIANCEFIELD_PATH),
        "--render",
        "--render-format", "mp4",
        "--render-output", str(output_dir),
    ]
    
    try:
        result = subprocess.run(cmd, cwd=str(WORK_DIR), check=True)
        print(f"✅ Successfully rendered: {fbx_name} + {ply_name}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to render: {fbx_name} + {ply_name}")
        print(f"Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def main():
    """Run all batch render jobs sequentially."""
    print("\n" + "="*70)
    print("BATCH RENDER: 15 TikTok Videos (3 FBX × 5 PLY)")
    print("Mode: Sequential with GPU rendering")
    print("="*70 + "\n")
    
    # Validate paths
    if not SCRIPT_PATH.exists():
        print(f"❌ Script not found: {SCRIPT_PATH}")
        return 1
    
    if not RADIANCEFIELD_PATH.exists():
        print(f"❌ RadianceField blend not found: {RADIANCEFIELD_PATH}")
        return 1
    
    if not CHARACTERS_DIR.exists():
        print(f"❌ Characters directory not found: {CHARACTERS_DIR}")
        return 1
    
    if not POINTCLOUDS_DIR.exists():
        print(f"❌ Point clouds directory not found: {POINTCLOUDS_DIR}")
        return 1
    
    # Create renders directory if it doesn't exist
    RENDERS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Calculate total renders
    total_renders = len(FBX_FILES) * len(PLY_FILES)
    completed = 0
    failed = 0
    
    # Run renders sequentially
    render_num = 1
    for fbx_file in FBX_FILES:
        for ply_file in PLY_FILES:
            if run_render(fbx_file, ply_file, render_num, total_renders):
                completed += 1
            else:
                failed += 1
            render_num += 1
    
    # Summary
    print(f"\n{'='*70}")
    print("BATCH RENDER COMPLETE")
    print(f"Total: {total_renders} | Completed: ✅ {completed} | Failed: ❌ {failed}")
    print(f"{'='*70}\n")
    
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
