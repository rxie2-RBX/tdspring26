#!/usr/bin/env python3
"""
Continue Sequential Batch Renderer - starts from job 2 (assuming job 1 is already running)
This script will wait briefly then process jobs 2-15.
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

# Remaining render queue: (fbx_name, ply_name) - starts from job 2
REMAINING_QUEUE = [
    # doozy-hiphop (4 remaining)
    ("doozy-hiphop.fbx", "Hydrant_vertical_point_cloud.ply"),  # Job 2
    ("doozy-hiphop.fbx", "David_Bust_point_cloud.ply"),  # Job 3
    ("doozy-hiphop.fbx", "McLaren_point_cloud.ply"),  # Job 4
    ("doozy-hiphop.fbx", "Panzernashorn_Tobler_point_cloud.ply"),  # Job 5
    # michelle-hiphop (5 videos)
    ("michelle-hiphop.fbx", "Mailbox_point_cloud.ply"),  # Job 6
    ("michelle-hiphop.fbx", "Hydrant_vertical_point_cloud.ply"),  # Job 7
    ("michelle-hiphop.fbx", "David_Bust_point_cloud.ply"),  # Job 8
    ("michelle-hiphop.fbx", "McLaren_point_cloud.ply"),  # Job 9
    ("michelle-hiphop.fbx", "Panzernashorn_Tobler_point_cloud.ply"),  # Job 10
    # mouse-hiphop (5 videos)
    ("mouse-hiphop.fbx", "Mailbox_point_cloud.ply"),  # Job 11
    ("mouse-hiphop.fbx", "Hydrant_vertical_point_cloud.ply"),  # Job 12
    ("mouse-hiphop.fbx", "David_Bust_point_cloud.ply"),  # Job 13
    ("mouse-hiphop.fbx", "McLaren_point_cloud.ply"),  # Job 14
    ("mouse-hiphop.fbx", "Panzernashorn_Tobler_point_cloud.ply"),  # Job 15
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
    log(f"JOB {job_num}/15: {fbx_name} + {ply_name}", "INFO")
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
        log(f"✅ Completed Job {job_num}: {fbx_name} + {ply_name}", "SUCCESS")
        return True
    except subprocess.CalledProcessError as e:
        log(f"❌ Failed with exit code {e.returncode}: {fbx_name} + {ply_name}", "ERROR")
        return False
    except Exception as e:
        log(f"❌ Unexpected error: {e}", "ERROR")
        return False

def main():
    """Run remaining render jobs sequentially."""
    log("=" * 70, "")
    log("CONTINUING BATCH RENDER: Jobs 2-15", "INFO")
    log("(Assuming Job 1 is already running or completed)", "INFO")
    log("=" * 70, "")
    
    # Validate paths
    if not SCRIPT_PATH.exists():
        log(f"Script not found: {SCRIPT_PATH}", "ERROR")
        return 1
    
    if not RADIANCEFIELD_PATH.exists():
        log(f"RadianceField blend not found: {RADIANCEFIELD_PATH}", "ERROR")
        return 1
    
    RENDERS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Wait for initial render to possibly complete
    log("⏳ Waiting 10 seconds before proceeding...", "INFO")
    time.sleep(10)
    
    completed = 0
    failed = 0
    failed_jobs = []
    
    # Process remaining queue starting from job 2
    for idx, (fbx_file, ply_file) in enumerate(REMAINING_QUEUE, 2):
        log(f"Processing job {idx}/15 ({idx-1}/{len(REMAINING_QUEUE)} in remaining queue)", "INFO")
        
        if render_single(fbx_file, ply_file, idx, 15):
            completed += 1
        else:
            failed += 1
            failed_jobs.append(f"Job {idx}: {fbx_file} + {ply_file}")
        
        # Pause between jobs
        if idx < 15:
            log("⏳ Pausing 5 seconds before next job...", "INFO")
            time.sleep(5)
    
    # Summary
    log("", "")
    log("=" * 70, "")
    log("REMAINING JOBS COMPLETE", "INFO")
    log(f"Jobs 2-15 | Completed: ✅ {completed} | Failed: ❌ {failed}", "INFO")
    
    if failed_jobs:
        log("Failed jobs:", "ERROR")
        for job in failed_jobs:
            log(f"  - {job}", "ERROR")
    
    log("=" * 70, "")
    log("⚠️  Remember to verify Job 1 completion!", "INFO")
    
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
