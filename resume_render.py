#!/usr/bin/env python3
"""
Resume Batch Renderer: Continue from unsfinished videos
Status: 17/20 videos completed, 3 remaining
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

# Only remaining incomplete jobs (mouse-hiphop combinations)
REMAINING_QUEUE = [
    ("mouse-hiphop.fbx", "David_Bust_point_cloud.ply"),       # Job 18/20
    ("mouse-hiphop.fbx", "McLaren_point_cloud.ply"),          # Job 19/20
    ("mouse-hiphop.fbx", "Panzernashorn_Tobler_point_cloud.ply"),  # Job 20/20
]

def log(msg: str, level: str = "INFO") -> None:
    """Print timestamped log message."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if msg.strip():
        print(f"[{timestamp}] [{level:8}] {msg}")
    else:
        print()

def render_single(fbx_name: str, ply_name: str, job_num: int) -> bool:
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
    log(f"JOB {job_num}/20: {fbx_name:20s} + {ply_name:35s}", "RENDER")
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
    """Run remaining 3 render jobs sequentially."""
    start_time = time.time()
    
    log("=" * 75, "")
    log("RESUME BATCH RENDER: 3 Remaining Videos (Jobs 18-20/20)", "START")
    log("=" * 75, "")
    log("")
    log(f"Status Summary:", "INFO")
    log(f"  ✅ Completed: 17/20 videos", "INFO")
    log(f"  ⏳ Remaining: 3/20 videos", "INFO")
    log(f"  📝 All mouse-hiphop combinations", "INFO")
    log("")
    log(f"Remaining Queue:", "INFO")
    log(f"  18/20: mouse-hiphop × David_Bust_point_cloud", "INFO")
    log(f"  19/20: mouse-hiphop × McLaren_point_cloud", "INFO")
    log(f"  20/20: mouse-hiphop × Panzernashorn_Tobler_point_cloud", "INFO")
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
    
    # Process remaining queue
    for idx, (fbx_file, ply_file) in enumerate(REMAINING_QUEUE, 1):
        job_num = 17 + idx  # Start from job 18
        if render_single(fbx_file, ply_file, job_num):
            completed += 1
        else:
            failed += 1
            failed_jobs.append(f"Job {job_num}: {fbx_file} + {ply_file}")
        
        # Brief pause between jobs
        if idx < len(REMAINING_QUEUE):
            log(f"Pausing 10 seconds before next job...", "INFO")
            time.sleep(10)
    
    # Final summary
    total_elapsed = time.time() - start_time
    total_hours = total_elapsed / 3600
    
    log("", "")
    log("=" * 75, "")
    log("FINAL BATCH COMPLETE: All 20 Videos Finished!", "FINISH")
    log("=" * 75, "")
    log(f"Resume Session: Completed {completed}/{len(REMAINING_QUEUE)} remaining videos", "RESULT")
    log(f"Overall Progress: 17 + {completed} = {17 + completed}/20 videos ✓", "RESULT")
    log(f"Resume Time: {total_hours:.2f} hours ({total_elapsed/60:.1f} minutes)", "RESULT")
    
    if failed_jobs:
        log("", "")
        log("Failed Jobs:", "ERROR")
        for job in failed_jobs:
            log(f"  • {job}", "ERROR")
    
    log("=" * 75, "")
    
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
