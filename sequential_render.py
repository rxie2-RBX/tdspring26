#!/usr/bin/env python3
"""
Sequential Batch Renderer with Queue Management
Waits for each render to complete before starting the next one.
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

# Render queue: (fbx_name, ply_name)
RENDER_QUEUE = [
    # doozy-hiphop (5 videos)
    ("doozy-hiphop.fbx", "Mailbox_point_cloud.ply"),
    ("doozy-hiphop.fbx", "Hydrant_vertical_point_cloud.ply"),
    ("doozy-hiphop.fbx", "David_Bust_point_cloud.ply"),
    ("doozy-hiphop.fbx", "McLaren_point_cloud.ply"),
    ("doozy-hiphop.fbx", "Panzernashorn_Tobler_point_cloud.ply"),
    # michelle-hiphop (5 videos)
    ("michelle-hiphop.fbx", "Mailbox_point_cloud.ply"),
    ("michelle-hiphop.fbx", "Hydrant_vertical_point_cloud.ply"),
    ("michelle-hiphop.fbx", "David_Bust_point_cloud.ply"),
    ("michelle-hiphop.fbx", "McLaren_point_cloud.ply"),
    ("michelle-hiphop.fbx", "Panzernashorn_Tobler_point_cloud.ply"),
    # mouse-hiphop (5 videos)
    ("mouse-hiphop.fbx", "Mailbox_point_cloud.ply"),
    ("mouse-hiphop.fbx", "Hydrant_vertical_point_cloud.ply"),
    ("mouse-hiphop.fbx", "David_Bust_point_cloud.ply"),
    ("mouse-hiphop.fbx", "McLaren_point_cloud.ply"),
    ("mouse-hiphop.fbx", "Panzernashorn_Tobler_point_cloud.ply"),
]

def log(msg: str, level: str = "INFO") -> None:
    """Print timestamped log message."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{level}] {msg}")

def render_single(fbx_name: str, ply_name: str, job_num: int, total_jobs: int) -> bool:
    """Run a single render job and wait for completion."""
    fbx_path = CHARACTERS_DIR / fbx_name
    ply_path = POINTCLOUDS_DIR / ply_name
    output_dir = RENDERS_DIR / f"{fbx_name.replace('.fbx', '')}_{ply_name.replace('.ply', '')}"
    
    if not fbx_path.exists():
        log(f"FBX not found: {fbx_path}", "ERROR")
        return False
    
    if not ply_path.exists():
        log(f"PLY not found: {ply_path}", "ERROR")
        return False
    
    log(f"", "")
    log("=" * 70, "")
    log(f"JOB {job_num}/{total_jobs}: {fbx_name} + {ply_name}", "INFO")
    log("=" * 70, "")
    
    # Build command
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
        log(f"Starting render: {fbx_name} + {ply_name}", "INFO")
        result = subprocess.run(cmd, cwd=str(WORK_DIR), check=True)
        log(f"✅ Completed: {fbx_name} + {ply_name}", "SUCCESS")
        return True
    except subprocess.CalledProcessError as e:
        log(f"❌ Failed with exit code {e.returncode}: {fbx_name} + {ply_name}", "ERROR")
        return False
    except Exception as e:
        log(f"❌ Unexpected error: {e}", "ERROR")
        return False

def main():
    """Run all render jobs sequentially, waiting for each to complete."""
    log("=" * 70, "")
    log("BATCH RENDER MANAGER: 15 TikTok Videos (Sequential)", "INFO")
    log("=" * 70, "")
    
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
        log(f"Processing job {idx}/{total}", "INFO")
        
        if render_single(fbx_file, ply_file, idx, total):
            completed += 1
        else:
            failed += 1
            failed_jobs.append(f"{fbx_file} + {ply_file}")
        
        # Brief pause between jobs
        if idx < total:
            log("Pausing 5 seconds before next job...", "INFO")
            time.sleep(5)
    
    # Summary
    log("", "")
    log("=" * 70, "")
    log("BATCH RENDER COMPLETE", "INFO")
    log(f"Total: {total} | Completed: ✅ {completed} | Failed: ❌ {failed}", "INFO")
    
    if failed_jobs:
        log("Failed jobs:", "ERROR")
        for job in failed_jobs:
            log(f"  - {job}", "ERROR")
    
    log("=" * 70, "")
    
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
