#!/usr/bin/env python3
"""
Complete Batch Renderer: 20 TikTok Videos
4 FBX characters × 5 point clouds = 20 total videos
Sequential rendering with GPU acceleration
"""

import subprocess
import sys
import time
from pathlib import Path
from datetime import datetime

WORK_DIR = Path(__file__).parent
SCRIPT_PATH = WORK_DIR / "exercises" / "project2" / "project2_ex1_fbx_tiktok.py"
RADIANCEFIELD_PATH = WORK_DIR / "exercises" / "project2" / "radiancefield.blend"
CHARACTERS_DIR = WORK_DIR / "characters"
POINTCLOUDS_DIR = WORK_DIR / "pointclouds"
RENDERS_DIR = WORK_DIR / "renders"

# Complete render queue: (fbx_name, ply_name)
RENDER_QUEUE = [
    # doozy-hiphop (5 videos, jobs 1-5)
    ("doozy-hiphop.fbx", "Mailbox_point_cloud.ply"),
    ("doozy-hiphop.fbx", "Hydrant_vertical_point_cloud.ply"),
    ("doozy-hiphop.fbx", "David_Bust_point_cloud.ply"),
    ("doozy-hiphop.fbx", "McLaren_point_cloud.ply"),
    ("doozy-hiphop.fbx", "Panzernashorn_Tobler_point_cloud.ply"),
    # vegas-hiphop (5 videos, jobs 6-10)
    ("vegas-hiphop.fbx", "Mailbox_point_cloud.ply"),
    ("vegas-hiphop.fbx", "Hydrant_vertical_point_cloud.ply"),
    ("vegas-hiphop.fbx", "David_Bust_point_cloud.ply"),
    ("vegas-hiphop.fbx", "McLaren_point_cloud.ply"),
    ("vegas-hiphop.fbx", "Panzernashorn_Tobler_point_cloud.ply"),
    # michelle-hiphop (5 videos, jobs 11-15)
    ("michelle-hiphop.fbx", "Mailbox_point_cloud.ply"),
    ("michelle-hiphop.fbx", "Hydrant_vertical_point_cloud.ply"),
    ("michelle-hiphop.fbx", "David_Bust_point_cloud.ply"),
    ("michelle-hiphop.fbx", "McLaren_point_cloud.ply"),
    ("michelle-hiphop.fbx", "Panzernashorn_Tobler_point_cloud.ply"),
    # mouse-hiphop (5 videos, jobs 16-20)
    ("mouse-hiphop.fbx", "Mailbox_point_cloud.ply"),
    ("mouse-hiphop.fbx", "Hydrant_vertical_point_cloud.ply"),
    ("mouse-hiphop.fbx", "David_Bust_point_cloud.ply"),
    ("mouse-hiphop.fbx", "McLaren_point_cloud.ply"),
    ("mouse-hiphop.fbx", "Panzernashorn_Tobler_point_cloud.ply"),
]

def log(msg: str, level: str = "INFO") -> None:
    """Print timestamped log message."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if msg.strip():
        print(f"[{timestamp}] [{level:8}] {msg}")
    else:
        print()

def render_single(fbx_name: str, ply_name: str, job_num: int, total_jobs: int) -> bool:
    """Run a single render job and wait for completion."""
    fbx_path = CHARACTERS_DIR / fbx_name
    ply_path = POINTCLOUDS_DIR / ply_name
    output_dir = RENDERS_DIR / f"{fbx_name.replace('.fbx', '')}_{ply_name.replace('.ply', '')}"
    
    if not fbx_path.exists():
        log(f"❌ FBX not found: {fbx_path}", "ERROR")
        return False
    
    if not ply_path.exists():
        log(f"❌ PLY not found: {ply_path}", "ERROR")
        return False
    
    log("", "")
    log("=" * 75, "")
    log(f"JOB {job_num:2d}/20: {fbx_name:20s} + {ply_name:35s}", "RENDER")
    log("=" * 75, "")
    
    # Build command with RadianceField
    cmd = [
        sys.executable,
        str(SCRIPT_PATH),
        str(fbx_path),
        "--pointcloud", str(ply_path),
        "--radiancefield", str(RADIANCEFIELD_PATH),
        "--render",
        "--render-format", "mp4",
        "--render-output", str(output_dir),
    ]
    
    try:
        log(f"Starting render...", "INFO")
        start_time = time.time()
        result = subprocess.run(cmd, cwd=str(WORK_DIR), check=True)
        elapsed = time.time() - start_time
        elapsed_min = elapsed / 60
        log(f"✅ COMPLETED in {elapsed_min:.1f} minutes", "SUCCESS")
        return True
    except subprocess.CalledProcessError as e:
        log(f"❌ FAILED with exit code {e.returncode}", "ERROR")
        return False
    except Exception as e:
        log(f"❌ UNEXPECTED ERROR: {e}", "ERROR")
        return False

def main():
    """Run all 20 render jobs sequentially."""
    start_time = time.time()
    
    log("=" * 75, "")
    log("BATCH RENDER MANAGER: 20 TikTok Videos (4 FBX × 5 PLY)", "START")
    log("=" * 75, "")
    log("")
    log(f"Render Queue:", "INFO")
    log(f"  • doozy-hiphop × 5 PLY files (Jobs 1-5)", "INFO")
    log(f"  • vegas-hiphop × 5 PLY files (Jobs 6-10)", "INFO")
    log(f"  • michelle-hiphop × 5 PLY files (Jobs 11-15)", "INFO")
    log(f"  • mouse-hiphop × 5 PLY files (Jobs 16-20)", "INFO")
    log("")
    log(f"Geometry Nodes: RadianceField ✓", "INFO")
    log(f"GPU Rendering: CUDA/OptiX ✓", "INFO")
    log(f"Output Format: MP4 (1080×1920, 25% resolution)", "INFO")
    log("")
    
    # Validate paths
    if not SCRIPT_PATH.exists():
        log(f"Script not found: {SCRIPT_PATH}", "ERROR")
        return 1
    
    if not RADIANCEFIELD_PATH.exists():
        log(f"RadianceField blend not found: {RADIANCEFIELD_PATH}", "ERROR")
        return 1
    
    RENDERS_DIR.mkdir(parents=True, exist_ok=True)
    
    completed = 0
    failed = 0
    failed_jobs = []
    
    # Process queue
    total = len(RENDER_QUEUE)
    for idx, (fbx_file, ply_file) in enumerate(RENDER_QUEUE, 1):
        if render_single(fbx_file, ply_file, idx, total):
            completed += 1
        else:
            failed += 1
            failed_jobs.append(f"Job {idx}: {fbx_file} + {ply_file}")
        
        # Brief pause between jobs
        if idx < total:
            log(f"Pausing 10 seconds before next job...", "INFO")
            time.sleep(10)
    
    # Final summary
    total_elapsed = time.time() - start_time
    total_hours = total_elapsed / 3600
    
    log("", "")
    log("=" * 75, "")
    log("BATCH RENDER COMPLETE", "FINISH")
    log("=" * 75, "")
    log(f"Total Jobs: {total} | Completed: ✅ {completed} | Failed: ❌ {failed}", "RESULT")
    log(f"Total Time: {total_hours:.2f} hours ({total_elapsed/60:.1f} minutes)", "RESULT")
    
    if failed_jobs:
        log("", "")
        log("Failed Jobs:", "ERROR")
        for job in failed_jobs:
            log(f"  • {job}", "ERROR")
    
    log("=" * 75, "")
    
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
