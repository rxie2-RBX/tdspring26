# Operation Log: Michelle-Mailbox Combined Scene

**Date:** March 13, 2026  
**Script:** `exercises/project2/project2_ex1_fbx_tiktok.py`

## Assets Selected

| Component | File | Source |
|-----------|------|--------|
| **Point Cloud** | `Mailbox_point_cloud.ply` | `pointclouds/` |
| **Character** | `michelle-hiphop.fbx` | `characters/` |
| **Output** | `michelle_mailbox_final_blend.blend` | workspace root |

## Point Cloud Specifications

- **Vertices:** 1,826,864 (isolated points, no faces)
- **Material:** Bright white (for viewport visibility)
- **RadianceField:** Auto-applied from `exercises/project2/radiancefield.blend`

## Transform Values Applied

### Point Cloud (Mailbox_point_cloud)
| Axis | Rotation | Position |
|------|----------|----------|
| X | 90.0° | 0.0m |
| Y | 0.0° | +1.50m (forward) |
| Z | 0.0° | +1.85m (upward) |

### Character (michelle-hiphop)
| Axis | Rotation | Position |
|------|----------|----------|
| X | 0.0° (default) | 0.0m (default) |
| Y | 0.0° (default) | 0.0m (default) |
| Z | 0.0° (default) | 0.0m (default) |

## Geometry Node Configuration

| Property | Value | Notes |
|----------|-------|-------|
| **RadianceField Applied** | Yes | Auto-detected & applied in Step 3 |
| **Bounding Box** | Skipped | No bbox parameters specified |
| **Node Group** | RadianceField | Loaded from radiancefield.blend |

## Camera & Animation Setup

- **Camera:** TikTokCamera (9:16 vertical aspect ratio)
- **Tracking Target:** Armature (mixamorig:Hips bone)
- **Animation Range:** Frames 1-184 (auto-detected from FBX)
- **Keyframes Baked:** 37 keyframes (at 5-frame intervals)
- **Lighting:** 3-point studio setup (Key, Fill, Rim lights)

## Issues & Resolutions

| Issue | Status | Resolution |
|-------|--------|-----------|
| HIPEW GPU initialization failed | ⚠️ Warning | Gracefully fell back to CUDA GPU rendering |
| FBX "User property type 'Short' not supported" | ⚠️ Warning | Expected for Mixamo FBX files—non-critical |
| Isolated vertices in point cloud | ✅ Expected | Material & RadianceField handle visualization |

## Result

✅ **Operation Successful**
- Blend file generated: `michelle_mailbox_final_blend.blend`
- All components loaded and configured
- Ready for animation preview and rendering
- No critical errors encountered
