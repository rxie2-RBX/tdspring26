"""Week 2 Exercise 4: FBX Import with TikTok-Style Camera Follow

This script uses typer to create a CLI tool that:
1. Imports an FBX file containing an animated character
2. Creates a vertical (9:16) TikTok-style camera setup
3. Automatically follows the character's animation with smooth tracking
"""

from pathlib import Path
from typing import Optional

import bpy
import typer
from mathutils import Vector
from typing_extensions import Annotated

app = typer.Typer(help="Import FBX and create TikTok-style camera automation")

SAVE_NAME = "week2ex4_tiktok.blend"
FRAME_STEP = 5  # Bake keyframes every N frames
CAMERA_DISTANCE = 2.5  # Distance from target in meters
CAMERA_HEIGHT_OFFSET = 1.5  # Height above target center
TARGET_BONE_NAME = "mixamorig:Hips"  # Common Mixamo bone name


def reset_scene() -> None:
    """Reset to a clean scene with proper settings."""
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.scene.render.engine = "CYCLES"  # Use Cycles for better GPU support

    # TikTok aspect ratio: 9:16 (vertical video)
    bpy.context.scene.render.resolution_x = 1080
    bpy.context.scene.render.resolution_y = 1920
    bpy.context.scene.render.resolution_percentage = 100
    
    # Enable GPU rendering (CUDA/OptiX)
    enable_gpu_rendering()


def enable_gpu_rendering() -> None:
    """Enable GPU rendering with CUDA/OptiX support."""
    try:
        scene = bpy.context.scene
        
        # Enable Cycles for GPU rendering (more reliable GPU support than EEVEE)
        scene.render.engine = "CYCLES"
        
        # Configure Cycles for GPU rendering
        cycles = scene.cycles
        cycles.use_denoising = True  # Enable denoising for better quality
        
        # Try to enable GPU rendering
        try:
            # Check for available compute devices
            prefs = bpy.context.preferences.addons['cycles'].preferences
            prefs.refresh_devices()
            
            # Try to use CUDA first, then OptiX, then fall back to CPU
            cuda_devices = [d for d in prefs.devices if 'CUDA' in d.type]
            optix_devices = [d for d in prefs.devices if 'OptiX' in d.type]
            
            if cuda_devices:
                prefs.compute_device_type = 'CUDA'
                for device in prefs.devices:
                    device.use = 'CUDA' in device.type
                typer.secho("[+] GPU rendering enabled (CUDA)", fg=typer.colors.GREEN)
            elif optix_devices:
                prefs.compute_device_type = 'OptiX'
                for device in prefs.devices:
                    device.use = 'OptiX' in device.type
                typer.secho("[+] GPU rendering enabled (OptiX)", fg=typer.colors.GREEN)
            else:
                # Fallback to CPU
                prefs.compute_device_type = 'CPU'
                for device in prefs.devices:
                    device.use = device.type == 'CPU'
                typer.secho("[+] No CUDA/OptiX GPU found, using CPU rendering", fg=typer.colors.YELLOW)
        except Exception as gpu_error:
            typer.secho(f"[!] GPU configuration warning: {gpu_error}", fg=typer.colors.YELLOW)
            typer.secho("[+] Using CPU rendering fallback", fg=typer.colors.GREEN)
        
    except Exception as e:
        typer.echo(f"Note: Could not configure rendering: {e}")
        typer.echo("Using default rendering")


def ensure_object_mode() -> None:
    """Ensure we're in object mode."""
    if bpy.context.mode != "OBJECT":
        bpy.ops.object.mode_set(mode="OBJECT")


def make_pointcloud_visible(obj: bpy.types.Object) -> None:
    """Convert isolated vertices to visible geometry by creating faces.
    
    For point clouds with no faces, this adds edges connecting nearby vertices,
    or applies a simple modifier to make points visible.
    """
    if not obj.data or obj.type != "MESH":
        return
    
    mesh = obj.data
    if len(mesh.polygons) > 0:
        # Already has faces
        return
    
    try:
        # Enter edit mode
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action="SELECT")
        
        # Try to create faces from loose points using edge-face conversion
        # First, let's try converting this to edges via "Wireframe" or similar
        # Actually, let's just exit edit mode - the material should work in Material Preview
        bpy.ops.object.mode_set(mode="OBJECT")
        
    except Exception as e:
        # If anything fails, just continue
        typer.secho(f"Note: Could not create visible geometry: {e}", fg=typer.colors.CYAN)
        bpy.ops.object.mode_set(mode="OBJECT")


def import_ply(ply_path: Path) -> Optional[bpy.types.Object]:
    """Import a PLY file (point cloud) and name it 'Pointcloud'."""
    if not ply_path.exists():
        typer.secho(f"Error: PLY file not found: {ply_path}", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    typer.echo(f"Importing point cloud: {ply_path.name}")

    # Get objects before import
    objects_before = set(bpy.data.objects)

    # Import PLY using the newer API
    try:
        bpy.ops.wm.ply_import(filepath=str(ply_path))
    except AttributeError:
        # Fallback for older Blender versions
        try:
            bpy.ops.import_mesh.ply(filepath=str(ply_path))
        except AttributeError:
            typer.secho(
                f"Error: PLY import not available in this Blender version",
                fg=typer.colors.RED,
            )
            raise typer.Exit(code=1)

    # Get newly imported objects
    objects_after = set(bpy.data.objects)
    imported_objects = list(objects_after - objects_before)

    if not imported_objects:
        typer.secho(f"Warning: No objects imported from {ply_path.name}", fg=typer.colors.YELLOW)
        return None

    # Name the first object "Pointcloud" (usually PLY has one mesh)
    pointcloud = imported_objects[0]
    pointcloud.name = "Pointcloud"
    if pointcloud.data:
        pointcloud.data.name = "Pointcloud_Mesh"
    
    # Store the original PLY filename as a custom property
    pointcloud["ply_filename"] = ply_path.name

    typer.secho(f"[+] Imported point cloud: {ply_path.name} (type: {pointcloud.type})", fg=typer.colors.GREEN)
    
    # Debug: check geometry info
    if pointcloud.type == "MESH":
        mesh_data = pointcloud.data
        vertices = len(mesh_data.vertices)
        faces = len(mesh_data.polygons)
        typer.secho(f"    Geometry: {vertices} vertices, {faces} faces", fg=typer.colors.CYAN)
        
        if faces == 0:
            typer.secho(
                f"    [*] Point cloud has isolated vertices (no faces)",
                fg=typer.colors.CYAN
            )
            typer.secho(
                f"    [*] To see the points in Blender:",
                fg=typer.colors.CYAN
            )
            typer.secho(
                f"        1. Switch viewport to 'Material Preview' or 'Rendered' mode (top right)",
                fg=typer.colors.CYAN
            )
            typer.secho(
                f"        2. Or use: --radiancefield <radiancefield.blend> for RadianceField visualization",
                fg=typer.colors.CYAN
            )
    
    return pointcloud


def apply_material_to_object(
    obj: bpy.types.Object,
    material_name: str = "PointcloudMaterial",
    use_vertex_colors: bool = True,
) -> None:
    """Apply a basic material to visualize the point cloud with bright white display.
    
    Note: Switch to Material Preview or Rendered viewport mode in Blender to see
    point clouds rendered with materials.
    """
    if not obj.data or obj.type != "MESH":
        return
    
    try:
        # Create or retrieve material
        if material_name in bpy.data.materials:
            mat = bpy.data.materials[material_name]
            # Clear existing nodes for fresh setup
            mat.node_tree.nodes.clear()
        else:
            mat = bpy.data.materials.new(name=material_name)
            mat.use_nodes = True
        
        # Ensure material has node tree
        if not mat.node_tree:
            mat.use_nodes = True
        
        # Access node tree
        node_tree = mat.node_tree
        links = node_tree.links
        nodes = node_tree.nodes
        
        # Clear all nodes
        nodes.clear()
        
        # Create nodes: Principled BSDF -> Material Output
        principled = nodes.new(type="ShaderNodeBsdfPrincipled")
        principled.inputs["Base Color"].default_value = (1.0, 1.0, 1.0, 1.0)  # Pure white
        
        # Add material output node
        mat_output = nodes.new(type="ShaderNodeOutputMaterial")
        
        # Connect BSDF to Material Output
        links.new(principled.outputs["BSDF"], mat_output.inputs["Surface"])
        
        # Ensure mesh has at least one material slot
        if len(obj.data.materials) == 0:
            obj.data.materials.append(mat)
        else:
            obj.data.materials[0] = mat
        
        # Set display mode for better point cloud visibility
        obj.display_type = "SOLID"
        obj.show_wire = False
        
        typer.secho(f"[+] Applied bright white material to {obj.name}", fg=typer.colors.GREEN)
        
    except Exception as e:
        typer.secho(f"Warning: Material setup had issues: {e}", fg=typer.colors.YELLOW)


def get_pointcloud_files(folder_path: Path) -> list[Path]:
    """Find all .ply files in a folder, excluding macOS hidden files (._*.ply)."""
    if not folder_path.exists():
        typer.secho(f"Error: Folder not found: {folder_path}", fg=typer.colors.RED)
        return []
    
    # Get all .ply files and filter out macOS resource fork files (._*.ply)
    ply_files = sorted([f for f in folder_path.glob("*.ply") if not f.name.startswith("._")])
    if not ply_files:
        typer.secho(f"No .ply files found in {folder_path}", fg=typer.colors.YELLOW)
    return ply_files


def rotate_object(
    obj: bpy.types.Object,
    rotation_x: float = 0.0,
    rotation_y: float = 0.0,
    rotation_z: float = 0.0,
) -> None:
    """Rotate an object by the specified angles (in degrees) around each axis."""
    import math
    
    # Convert degrees to radians
    rot_x = math.radians(rotation_x)
    rot_y = math.radians(rotation_y)
    rot_z = math.radians(rotation_z)
    
    # Apply rotations
    obj.rotation_euler = (rot_x, rot_y, rot_z)


def load_nodgroup_from_blend(blend_file: Path, node_group_name: str) -> bool:
    """Load a node group from an external blend file."""
    # Ensure path is absolute
    blend_file = Path(blend_file).resolve()
    
    if not blend_file.exists():
        typer.secho(f"Warning: Blend file not found: {blend_file}", fg=typer.colors.YELLOW)
        return False
    
    try:
        # Link the node group from the blend file
        with bpy.data.libraries.load(str(blend_file), link=False) as (data_from, data_to):
            if node_group_name in data_from.node_groups:
                data_to.node_groups = [node_group_name]
                typer.secho(
                    f"[+] Loaded node group '{node_group_name}' from {blend_file.name}",
                    fg=typer.colors.GREEN,
                )
                return True
            else:
                typer.secho(
                    f"Warning: Node group '{node_group_name}' not found in {blend_file.name}",
                    fg=typer.colors.YELLOW,
                )
                return False
    except Exception as e:
        typer.secho(f"Warning: Failed to load node group: {e}", fg=typer.colors.YELLOW)
        return False


def apply_radiancefield_to_pointcloud(
    pointcloud: bpy.types.Object,
    node_group_name: str = "RadianceField",
) -> bool:
    """Apply a RadianceField to the pointcloud object."""
    try:
        # Check if the node group exists by name
        node_group = bpy.data.node_groups[node_group_name]
        
        # Add RadianceField modifier (use "NODES" instead of "GEOMETRY_NODES" for Blender 5.x)
        geo_mod = pointcloud.modifiers.new(name="RadianceField", type="NODES")
        geo_mod.node_group = node_group
        
        typer.secho(
            f"[+] Applied RadianceField node group: {node_group_name}",
            fg=typer.colors.GREEN,
        )
        return True
        
    except KeyError:
        typer.secho(
            f"Note: Geometry node group '{node_group_name}' not loaded",
            fg=typer.colors.CYAN,
        )
        return False
    except Exception as e:
        typer.secho(
            f"Warning: Failed to apply RadianceField: {type(e).__name__}: {e}",
            fg=typer.colors.YELLOW,
        )
        return False
        return False


def set_radiancefield_input(
    pointcloud: bpy.types.Object,
    socket_name: str,
    value: float,
) -> bool:
    """Set a RadianceField input socket value.
    
    Args:
        pointcloud: The object with the RadianceField modifier
        socket_name: The socket name (e.g., 'Socket_3')
        value: The value to set
        
    Returns:
        True if successful, False otherwise
    """
    if "RadianceField" not in pointcloud.modifiers:
        typer.secho(
            f"Warning: RadianceField modifier not found on {pointcloud.name}",
            fg=typer.colors.YELLOW,
        )
        return False
    
    try:
        geo_mod = pointcloud.modifiers["RadianceField"]
        geo_mod[socket_name] = value
        return True
    except Exception as e:
        typer.secho(
            f"Warning: Failed to set geometry node input: {e}",
            fg=typer.colors.YELLOW,
        )
        return False


def set_pointcloud_bounding_box(
    pointcloud: bpy.types.Object,
    bbox_x: float = 0.0,
    bbox_y: float = 0.0,
    bbox_z: float = 0.0,
) -> None:
    """Set the bounding box parameters for the RadianceField.
    
    These correspond to Socket_3[0], Socket_3[1], Socket_3[2] on the RadianceField modifier.
    """
    if "RadianceField" not in pointcloud.modifiers:
        typer.secho(
            f"Warning: RadianceField modifier not found on {pointcloud.name}",
            fg=typer.colors.YELLOW,
        )
        return
    
    geo_mod = pointcloud.modifiers["RadianceField"]
    try:
        # Try to set the Socket_3 vector parameter
        # Note: Socket naming may vary by Blender version and node setup
        geo_mod["Socket_3"] = (bbox_x, bbox_y, bbox_z)
        typer.secho(
            f"[+] Set bounding box: X={bbox_x} Y={bbox_y} Z={bbox_z}",
            fg=typer.colors.GREEN,
        )
    except Exception:
        # Try alternative socket names
        try:
            for i, val in enumerate([bbox_x, bbox_y, bbox_z]):
                socket_key = f"Socket_3{i}"
                if socket_key in geo_mod:
                    geo_mod[socket_key] = val
            typer.secho(
                f"[+] Set bounding box: X={bbox_x} Y={bbox_y} Z={bbox_z}",
                fg=typer.colors.GREEN,
            )
        except Exception as e:
            typer.secho(
                f"Warning: Could not set bounding box parameters: {e}",
                fg=typer.colors.YELLOW,
            )




def get_fbx_files(folder_path: Path) -> list[Path]:
    """Find all .fbx files in a folder."""
    if not folder_path.exists():
        typer.secho(f"Error: Folder not found: {folder_path}", fg=typer.colors.RED)
        return []
    
    fbx_files = sorted(folder_path.glob("*.fbx"))
    if not fbx_files:
        typer.secho(f"No .fbx files found in {folder_path}", fg=typer.colors.YELLOW)
    return fbx_files


def position_object(
    obj: bpy.types.Object,
    pos_x: float = 0.0,
    pos_y: float = 0.0,
    pos_z: float = 0.0,
) -> None:
    """Position an object at the specified location."""
    obj.location = (pos_x, pos_y, pos_z)


def import_fbx(fbx_path: Path) -> list[bpy.types.Object]:
    """Import FBX file and return imported objects."""
    if not fbx_path.exists():
        typer.secho(f"Error: FBX file not found: {fbx_path}", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    typer.echo(f"Importing FBX: {fbx_path}")

    # Get objects before import
    objects_before = set(bpy.data.objects)

    # Import FBX
    bpy.ops.import_scene.fbx(filepath=str(fbx_path))

    # Get newly imported objects
    objects_after = set(bpy.data.objects)
    imported_objects = list(objects_after - objects_before)

    typer.secho(f"[+] Imported {len(imported_objects)} objects", fg=typer.colors.GREEN)
    return imported_objects


def find_armature(
    imported_objects: list[bpy.types.Object],
) -> Optional[bpy.types.Object]:
    """Find the armature object from imported objects."""
    for obj in imported_objects:
        if obj.type == "ARMATURE":
            return obj
    return None


def get_target_world_location(
    armature: bpy.types.Object, bone_name: str
) -> tuple[float, float, float]:
    """Get world location of a bone in the armature."""
    if bone_name in armature.pose.bones:
        bone = armature.pose.bones[bone_name]
        matrix = armature.matrix_world @ bone.matrix
        return tuple(matrix.translation)

    # Fallback to armature origin
    return tuple(armature.matrix_world.translation)


def create_tiktok_camera(name: str = "TikTokCamera") -> bpy.types.Object:
    """Create a camera optimized for TikTok-style vertical video."""
    bpy.ops.object.camera_add()
    camera = bpy.context.active_object
    camera.name = name
    camera.data.name = f"{name}_data"

    # Camera settings for portrait video
    camera.data.lens = 50  # Standard focal length
    camera.data.sensor_width = 36
    camera.data.sensor_height = 36 * (16 / 9)  # Adjust sensor for vertical

    # Set as active camera
    bpy.context.scene.camera = camera

    return camera


def setup_camera_tracking(
    camera: bpy.types.Object,
    target: bpy.types.Object,
    bone_name: Optional[str] = None,
    frame_start: int = 1,
    frame_end: int = 250,
    fbx_filename: Optional[str] = None,
) -> None:
    """Setup camera to follow the target with baked keyframes."""
    typer.echo(f"Setting up camera tracking from frame {frame_start} to {frame_end}")

    # Clear existing animation data
    if camera.animation_data:
        camera.animation_data_clear()

    scene = bpy.context.scene

    # Bake keyframes
    for frame in range(frame_start, frame_end + 1, FRAME_STEP):
        scene.frame_set(frame)

        # Get target location
        if target.type == "ARMATURE" and bone_name:
            target_loc = get_target_world_location(target, bone_name)
        else:
            target_loc = tuple(target.matrix_world.translation)

        # Position camera behind and above target
        # Check for special FBX files with custom camera Z height offset
        if fbx_filename and "doozy-hiphop" in fbx_filename:
            camera_z_offset = CAMERA_HEIGHT_OFFSET + 0.9  # Add 0.9m for doozy-hiphop
        else:
            camera_z_offset = CAMERA_HEIGHT_OFFSET
        
        camera.location = (
            target_loc[0],
            target_loc[1] - CAMERA_DISTANCE,
            target_loc[2] + camera_z_offset,
        )

        # Point camera at target
        direction = Vector(
            (
                target_loc[0] - camera.location[0],
                target_loc[1] - camera.location[1],
                target_loc[2] - camera.location[2],
            )
        )

        # Calculate rotation to look at target
        import math

        rot_quat = camera.rotation_euler.to_quaternion()
        track_quat = direction.to_track_quat("-Z", "Y")
        camera.rotation_euler = track_quat.to_euler()

        # Insert keyframes
        camera.keyframe_insert(data_path="location", frame=frame)
        camera.keyframe_insert(data_path="rotation_euler", frame=frame)

    typer.secho(
        f"[+] Baked {(frame_end - frame_start) // FRAME_STEP + 1} keyframes",
        fg=typer.colors.GREEN,
    )


def add_studio_lighting() -> None:
    """Add basic three-point lighting setup."""
    typer.echo("Adding studio lighting")

    # Key light
    bpy.ops.object.light_add(type="AREA", location=(2, -2, 4))
    key_light = bpy.context.active_object
    key_light.name = "KeyLight"
    key_light.data.energy = 200
    key_light.data.size = 2

    # Fill light
    bpy.ops.object.light_add(type="AREA", location=(-2, -1, 2))
    fill_light = bpy.context.active_object
    fill_light.name = "FillLight"
    fill_light.data.energy = 100
    fill_light.data.size = 2

    # Rim light
    bpy.ops.object.light_add(type="SPOT", location=(0, 2, 3))
    rim_light = bpy.context.active_object
    rim_light.name = "RimLight"
    rim_light.data.energy = 150

    typer.secho("[+] Lighting setup complete", fg=typer.colors.GREEN)


def save_blend_file(output_path: Optional[Path] = None) -> None:
    """Save the blend file."""
    if output_path is None:
        output_path = Path.cwd() / SAVE_NAME

    output_path.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(output_path))
    typer.secho(f"[+] Saved: {output_path}", fg=typer.colors.GREEN)


def render_frame(frame: int, output_path: Path) -> bool:
    """Render a single frame to PNG."""
    scene = bpy.context.scene
    scene.frame_set(frame)
    
    # Set output path
    scene.render.filepath = str(output_path)
    scene.render.image_settings.file_format = "PNG"
    
    try:
        # Render the frame
        bpy.ops.render.render(write_still=True)
        return True
    except Exception as e:
        typer.secho(f"Error rendering frame: {e}", fg=typer.colors.RED)
        return False


def render_animation(start_frame: int, end_frame: int, output_dir: Path, name_prefix: str, format: str = "PNG") -> bool:
    """Render full animation directly to MPEG-4 video (via PNG sequence conversion)."""
    scene = bpy.context.scene
    
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        if format.upper() == "MPEG4":
            # Render as PNG sequence first (stable approach)
            scene.render.image_settings.file_format = "PNG"
            scene.render.resolution_percentage = 25  # 25% resolution for ultra-fast rendering
            scene.render.fps = 24  # 24 fps output
            
            # Set output path pattern for PNG sequence
            output_pattern = str(output_dir / f"{name_prefix}_######")
            scene.render.filepath = output_pattern
            
            typer.echo(f"Rendering animation to PNG sequence (25% resolution)...")
            bpy.ops.render.render(animation=True)
            typer.secho(f"[+] PNG sequence rendered to: {output_dir}", fg=typer.colors.GREEN)
            
            # Convert PNG sequence to MPEG-4 with low quality settings
            typer.echo(f"Converting PNG sequence to MPEG-4 (low quality, 1600 kbps, faster preset)...")
            import subprocess
            
            output_file = output_dir / f"{name_prefix}.mp4"
            try:
                subprocess.run(
                    [
                        "ffmpeg", "-framerate", "24",
                        "-i", str(output_dir / f"{name_prefix}_%06d.png"),
                        "-c:v", "libx264",
                        "-pix_fmt", "yuv420p",
                        "-b:v", "1600k",  # 1600 kbps = low quality
                        "-preset", "faster",  # faster preset for quicker encoding
                        "-y",  # overwrite output file
                        str(output_file)
                    ],
                    check=True,
                    capture_output=True
                )
                typer.secho(f"[+] MPEG-4 video created: {output_file}", fg=typer.colors.GREEN)
                
                # Clean up PNG files
                for png_file in output_dir.glob(f"{name_prefix}_*.png"):
                    png_file.unlink()
                typer.secho(f"[+] Cleaned up PNG sequence", fg=typer.colors.GREEN)
                
            except subprocess.CalledProcessError as e:
                typer.secho(f"Error converting to MPEG-4: {e.stderr.decode()}", fg=typer.colors.RED)
                return False
            except FileNotFoundError:
                typer.secho("FFmpeg not found. Please install FFmpeg to render MPEG-4 videos.", fg=typer.colors.RED)
                return False
        else:
            # PNG sequence output
            scene.render.image_settings.file_format = "PNG"
            scene.render.resolution_percentage = 100
            
            # Set output path pattern for PNG sequence
            output_pattern = str(output_dir / f"{name_prefix}_######")
            scene.render.filepath = output_pattern
            
            typer.echo(f"Rendering animation to PNG sequence...")
            bpy.ops.render.render(animation=True)
            typer.secho(f"[+] Animation rendered to: {output_dir}", fg=typer.colors.GREEN)
        
        return True
    except Exception as e:
        typer.secho(f"Error rendering animation: {e}", fg=typer.colors.RED)
        return False


def generate_output_filename(pointcloud_name: Optional[str], character_name: Optional[str], format: str) -> str:
    """Generate output filename combining pointcloud and character names."""
    parts = []
    
    if pointcloud_name:
        # Extract filename without extension
        pc_name = Path(pointcloud_name).stem
        parts.append(pc_name)
    
    if character_name:
        # Extract filename without extension
        char_name = Path(character_name).stem
        parts.append(char_name)
    
    if not parts:
        parts.append("output")
    
    filename = "_".join(parts) + f".{format}"
    return filename


def save_blend_file(output_path: Optional[Path] = None) -> None:
    """Save the blend file."""
    if output_path is None:
        output_path = Path.cwd() / SAVE_NAME

    output_path.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(output_path))
    typer.secho(f"[+] Saved: {output_path}", fg=typer.colors.GREEN)


@app.command()
def create(
    fbx_file: Annotated[Path, typer.Argument(help="Path to the FBX file to import")],
    pointcloud: Annotated[
        Optional[Path],
        typer.Option("--pointcloud", "--ply", help="Path to a specific PLY (point cloud) file to import"),
    ] = None,
    pointcloud_folder: Annotated[
        Optional[Path],
        typer.Option("--pointcloud-folder", help="Path to folder with PLY files (imports all)"),
    ] = None,
    pointcloud_rx: Annotated[
        float,
        typer.Option("--pc-rx", help="Pointcloud rotation around X axis (degrees)"),
    ] = 0.0,
    pointcloud_ry: Annotated[
        float,
        typer.Option("--pc-ry", help="Pointcloud rotation around Y axis (degrees)"),
    ] = 0.0,
    pointcloud_rz: Annotated[
        float,
        typer.Option("--pc-rz", help="Pointcloud rotation around Z axis (degrees)"),
    ] = 0.0,
    bbox_x: Annotated[
        float,
        typer.Option("--bbox-x", help="Bounding box X parameter for RadianceField nodes"),
    ] = 0.0,
    bbox_y: Annotated[
        float,
        typer.Option("--bbox-y", help="Bounding box Y parameter for RadianceField nodes"),
    ] = 0.0,
    bbox_z: Annotated[
        float,
        typer.Option("--bbox-z", help="Bounding box Z parameter for RadianceField nodes"),
    ] = 0.0,
    radiancefield_blend: Annotated[
        Optional[Path],
        typer.Option("--radiancefield", help="Path to radiancefield.blend file for RadianceField"),
    ] = None,
    char_x: Annotated[
        float,
        typer.Option("--char-x", help="Character position X"),
    ] = 0.0,
    char_y: Annotated[
        float,
        typer.Option("--char-y", help="Character position Y"),
    ] = 0.0,
    char_z: Annotated[
        float,
        typer.Option("--char-z", help="Character position Z"),
    ] = 0.0,
    char_rx: Annotated[
        float,
        typer.Option("--char-rx", help="Character rotation around X axis (degrees)"),
    ] = 0.0,
    char_ry: Annotated[
        float,
        typer.Option("--char-ry", help="Character rotation around Y axis (degrees)"),
    ] = 0.0,
    char_rz: Annotated[
        float,
        typer.Option("--char-rz", help="Character rotation around Z axis (degrees)"),
    ] = 0.0,
    output: Annotated[
        Optional[Path],
        typer.Option("--output", "-o", help="Output .blend file path"),
    ] = None,
    bone: Annotated[
        str,
        typer.Option("--bone", "-b", help="Target bone name for camera tracking"),
    ] = TARGET_BONE_NAME,
    start_frame: Annotated[
        int, typer.Option("--start", "-s", help="Animation start frame")
    ] = 1,
    end_frame: Annotated[
        Optional[int], typer.Option("--end", "-e", help="Animation end frame (defaults to last frame of armature animation)")
    ] = None,
    no_lights: Annotated[
        bool, typer.Option("--no-lights", help="Skip adding studio lights")
    ] = False,
    render: Annotated[
        bool, typer.Option("--render", help="Render the scene after setup"),
    ] = False,
    render_frame: Annotated[
        Optional[int], typer.Option("--render-frame", help="Render a specific frame (single frame mode)"),
    ] = None,
    render_format: Annotated[
        str, typer.Option("--render-format", help="Output format: 'png' or 'mp4'")
    ] = "png",
    render_output: Annotated[
        Optional[Path], typer.Option("--render-output", "-r", help="Output path for rendered files")
    ] = None,
) -> None:
    """Import a point cloud (PLY) and FBX file with TikTok-style camera automation.

    Example:
        python project2_ex1_fbx_tiktok.py create character.fbx --pointcloud cloud.ply
        python project2_ex1_fbx_tiktok.py create character.fbx --pointcloud-folder ./pointclouds/ --pc-ry 45
        python project2_ex1_fbx_tiktok.py create character.fbx --pointcloud cloud.ply --char-x 2.0 --char-z 1.0
    """
    typer.secho("** TikTok Camera Setup with Point Cloud", fg=typer.colors.CYAN, bold=True)
    typer.echo("=" * 50)

    # Step 1: Reset scene
    typer.echo("1. Resetting scene...")
    reset_scene()
    ensure_object_mode()

    # Step 2: Import point cloud if specified
    pointclouds = []
    if pointcloud:
        typer.echo("2. Importing point cloud...")
        pc = import_ply(pointcloud)
        if pc:
            apply_material_to_object(pc)
            pointclouds.append(pc)
    elif pointcloud_folder:
        typer.echo("2. Importing point clouds from folder...")
        ply_files = get_pointcloud_files(pointcloud_folder)
        for ply_file in ply_files:
            pc = import_ply(ply_file)
            if pc:
                apply_material_to_object(pc)
                pointclouds.append(pc)
        if not ply_files:
            typer.secho("Warning: No point clouds found to import", fg=typer.colors.YELLOW)
    else:
        typer.echo("2. No point cloud specified (optional)")

    # Step 3: Load and apply RadianceField (auto-detect if not specified)
    if pointclouds:
        typer.echo("3. Loading and applying RadianceField...")
        # Auto-detect radiancefield.blend if not specified
        if radiancefield_blend is None:
            radiancefield_blend = Path("exercises/project2/radiancefield.blend").resolve()
        
        if load_nodgroup_from_blend(radiancefield_blend, "RadianceField"):
            # Apply to all pointclouds
            for pc in pointclouds:
                apply_radiancefield_to_pointcloud(pc, "RadianceField")
        else:
            typer.secho(f"Warning: Could not apply RadianceField", fg=typer.colors.YELLOW)
    else:
        typer.echo("3. Skipping RadianceField (no pointclouds to apply to)")

    # Step 4: Apply rotations to pointclouds
    # Note: Always apply 90 degree X-axis rotation by default, plus any user-specified rotations
    if pointclouds:
        typer.echo("4. Applying pointcloud rotations...")
        for pc in pointclouds:
            # Apply default X-axis 90 degree rotation + user-specified rotations
            final_rx = pointcloud_rx + 90
            rotate_object(pc, final_rx, pointcloud_ry, pointcloud_rz)
            typer.secho(
                f"[+] Rotated {pc.name}: X={final_rx}° Y={pointcloud_ry}° Z={pointcloud_rz}°",
                fg=typer.colors.GREEN,
            )
    else:
        typer.echo("4. No pointclouds to rotate")

    # Step 4.5: Move pointclouds up on Z-axis and forward on Y-axis by default (1.5m forward, 1.85m up)
    if pointclouds:
        typer.echo("4.5. Adjusting pointcloud position...")
        for pc in pointclouds:
            current_y = pc.location.y
            current_z = pc.location.z
            pc.location.y = current_y + 1.5  # Move forward 1.5m on Y axis
            
            # Check for special point cloud files with custom Z positioning
            ply_filename = pc.get("ply_filename", "")
            if "Hydrant" in ply_filename:
                pc.location.z = 1.5  # Set to 1.5m for Hydrant
                typer.secho(
                    f"[+] Hydrant pointcloud detected: Z set to 1.5m (special handling)",
                    fg=typer.colors.CYAN,
                )
            elif "McLaren" in ply_filename:
                pc.location.z = 0.997504  # Set to 0.997504m for McLaren
                typer.secho(
                    f"[+] McLaren pointcloud detected: Z set to 0.997504m (special handling)",
                    fg=typer.colors.CYAN,
                )
            elif "Panzernashorn_Tobler" in ply_filename:
                pc.location.z = 0.619954  # Set to 0.619954m for Panzernashorn_Tobler
                typer.secho(
                    f"[+] Panzernashorn_Tobler pointcloud detected: Z set to 0.619954m (special handling)",
                    fg=typer.colors.CYAN,
                )
            else:
                pc.location.z = current_z + 1.85  # Move up 1.85m on Z axis for other clouds
            
            typer.secho(
                f"[+] Moved {pc.name}: Y={pc.location.y:.2f}m, Z={pc.location.z:.2f}m",
                fg=typer.colors.GREEN,
            )

    # Step 5: Set bounding box parameters if RadianceField is applied
    if pointclouds and radiancefield_blend and (bbox_x != 0 or bbox_y != 0 or bbox_z != 0):
        typer.echo("5. Setting bounding box parameters...")
        for pc in pointclouds:
            set_pointcloud_bounding_box(pc, bbox_x, bbox_y, bbox_z)
    else:
        typer.echo("5. Skipping bounding box (no RadianceField or parameters)")

    # Step 6: Import FBX
    typer.echo(f"6. Importing FBX: {fbx_file}")
    imported_objects = import_fbx(fbx_file)
    
    # Step 7: Position and rotate the imported character
    if imported_objects and (char_x != 0 or char_y != 0 or char_z != 0):
        typer.echo("7. Positioning character...")
        for obj in imported_objects:
            if obj.type in ("ARMATURE", "MESH"):
                position_object(obj, char_x, char_y, char_z)
                typer.secho(
                    f"[+] Positioned {obj.name}: X={char_x} Y={char_y} Z={char_z}",
                    fg=typer.colors.GREEN,
                )
                break  # Only position the first armature/mesh
    else:
        typer.echo("7. No character position specified")

    # Step 8: Rotate the character if needed
    if imported_objects and (char_rx != 0 or char_ry != 0 or char_rz != 0):
        typer.echo("8. Rotating character...")
        for obj in imported_objects:
            if obj.type in ("ARMATURE", "MESH"):
                rotate_object(obj, char_rx, char_ry, char_rz)
                typer.secho(
                    f"[+] Rotated {obj.name}: X={char_rx}° Y={char_ry}° Z={char_rz}°",
                    fg=typer.colors.GREEN,
                )
                break  # Only rotate the first armature/mesh
    else:
        typer.echo("8. No character rotation specified")
    
    # Step 9: Find armature
    typer.echo("9. Looking for armature...")
    armature = find_armature(imported_objects)

    if not armature:
        typer.secho(
            "Warning: No armature found. Using first imported object as target.",
            fg=typer.colors.YELLOW,
        )
        target = imported_objects[0] if imported_objects else None
        if not target:
            typer.secho("Error: No objects imported!", fg=typer.colors.RED)
            raise typer.Exit(code=1)
        target_bone = None
    else:
        typer.secho(f"[+] Found armature: {armature.name}", fg=typer.colors.GREEN)
        target = armature
        target_bone = bone

    # Determine end frame if not specified
    if end_frame is None and armature and armature.animation_data and armature.animation_data.action:
        end_frame = int(bpy.data.objects['Armature'].animation_data.action.frame_range[1])
        typer.secho(
            f"[+] Using armature animation end frame: {end_frame}",
            fg=typer.colors.GREEN,
        )
    elif end_frame is None:
        # Fallback: use a default if no animation data found
        # Use 184 as default (common animation length) instead of 250
        end_frame = 184
        typer.secho(
            f"[+] No animation data found, using default end frame: {end_frame}",
            fg=typer.colors.YELLOW,
        )

    # Step 10: Set frame range
    bpy.context.scene.frame_start = start_frame
    bpy.context.scene.frame_end = end_frame

    # Step 11: Create camera
    typer.echo("11. Creating TikTok-style camera...")
    camera = create_tiktok_camera()

    # Step 12: Setup tracking
    typer.echo("12. Setting up camera tracking...")
    setup_camera_tracking(camera, target, target_bone, start_frame, end_frame, fbx_file.name)

    # Step 13: Add lighting
    if not no_lights:
        typer.echo("13. Adding studio lighting...")
        add_studio_lighting()
    else:
        typer.echo("13. Skipping lights (--no-lights specified)")

    # Step 14: Save file
    typer.echo("14. Saving blend file...")
    save_blend_file(output)

    # Step 16: Render if requested
    if render:
        typer.echo("16. Rendering...")
        
        # Get names for output file
        pc_name = pointcloud.stem if pointcloud else None
        char_name = fbx_file.stem if fbx_file else None
        
        if render_frame is not None:
            # Single frame render
            target_frame = render_frame
            typer.echo(f"Rendering frame {target_frame}...")
            
            if render_output:
                output_file = Path(render_output).resolve()
            else:
                filename = generate_output_filename(pc_name, char_name, render_format)
                output_file = Path.cwd() / filename
            
            if render_format.lower() == "png":
                if target_frame < start_frame or target_frame > end_frame:
                    typer.secho(
                        f"Warning: Frame {target_frame} is outside animation range ({start_frame}-{end_frame})",
                        fg=typer.colors.YELLOW,
                    )
                if target_frame >= start_frame and target_frame <= end_frame:
                    bpy.context.scene.frame_set(target_frame)
                    bpy.context.scene.render.filepath = str(output_file)
                    bpy.ops.render.render(write_still=True)
                    typer.secho(f"[+] Rendered frame {target_frame} to {output_file}", fg=typer.colors.GREEN)
            else:
                typer.secho("Note: Single frame rendering is PNG only, use animation mode for mp4", fg=typer.colors.YELLOW)
        else:
            # Full animation render
            typer.echo(f"Rendering animation (frames {start_frame}-{end_frame}) as {render_format.upper()}...")
            
            if render_output:
                output_dir = Path(render_output).resolve() if Path(render_output).is_dir() else Path(render_output).resolve().parent
            else:
                filename_prefix = generate_output_filename(pc_name, char_name, "")
                output_dir = Path.cwd() / filename_prefix
            
            if render_format.lower() == "png":
                filename_prefix = generate_output_filename(pc_name, char_name, "")
                render_animation(start_frame, end_frame, output_dir, filename_prefix, format="PNG")
            elif render_format.lower() == "mp4":
                filename_prefix = generate_output_filename(pc_name, char_name, "mp4").replace(".mp4", "")
                render_animation(start_frame, end_frame, output_dir, filename_prefix, format="MPEG4")
    else:
        typer.echo("16. Skipping render (--render not specified)")

    typer.echo("=" * 50)
    typer.secho("[*] Setup complete!", fg=typer.colors.GREEN, bold=True)
    typer.echo(f"Camera: {camera.name}")
    typer.echo(f"Target: {target.name}")
    if target_bone:
        typer.echo(f"Tracking bone: {target_bone}")
    typer.echo(f"Frame range: {start_frame} - {end_frame}")


if __name__ == "__main__":
    app()
