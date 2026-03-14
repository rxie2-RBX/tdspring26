"""Combine character FBX with point cloud and apply RadianceField.

Usage:
    python combine_character_pointcloud.py --fbx characters/michelle-hiphop.fbx --pointcloud pointclouds/Mailbox_point_cloud.blend [--output OUTPUT.blend]
"""

from pathlib import Path
from typing import Optional

import bpy
import typer
from typing_extensions import Annotated

app = typer.Typer(help="Combine character FBX with point cloud")


def reset_scene() -> None:
    """Reset to a clean scene with proper settings."""
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.scene.render.engine = "CYCLES"
    
    # Standard viewport settings
    bpy.context.scene.render.resolution_x = 1920
    bpy.context.scene.render.resolution_y = 1080
    bpy.context.scene.render.resolution_percentage = 100


def import_fbx(fbx_path: Path) -> list[bpy.types.Object]:
    """Import FBX file and return imported objects."""
    if not fbx_path.exists():
        typer.secho(f"Error: FBX file not found: {fbx_path}", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    typer.echo(f"Importing FBX: {fbx_path.name}")

    # Get objects before import
    objects_before = set(bpy.data.objects)

    # Import FBX
    bpy.ops.import_scene.fbx(filepath=str(fbx_path))

    # Get newly imported objects
    objects_after = set(bpy.data.objects)
    imported_objects = list(objects_after - objects_before)

    typer.secho(f"[+] Imported {len(imported_objects)} objects from FBX", fg=typer.colors.GREEN)
    for obj in imported_objects:
        if obj.type == "ARMATURE":
            typer.secho(f"    - Armature: {obj.name}", fg=typer.colors.CYAN)
    
    return imported_objects


def import_blend(blend_path: Path) -> list[bpy.types.Object]:
    """Import all objects from a blend file using append."""
    if not blend_path.exists():
        typer.secho(f"Error: Blend file not found: {blend_path}", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    typer.echo(f"Importing from blend file: {blend_path.name}")

    # Get objects before import
    objects_before = set(bpy.data.objects)

    # Load all objects from blend file
    with bpy.data.libraries.load(str(blend_path), link=False) as (data_from, data_to):
        data_to.objects = data_from.objects

    # Get newly imported objects
    objects_after = set(bpy.data.objects)
    imported_objects = list(objects_after - objects_before)

    typer.secho(f"[+] Imported {len(imported_objects)} objects from blend file", fg=typer.colors.GREEN)
    for obj in imported_objects:
        typer.secho(f"    - {obj.type}: {obj.name}", fg=typer.colors.CYAN)
    
    # Link imported objects to scene
    for obj in imported_objects:
        if obj.name not in bpy.context.scene.collection.objects:
            bpy.context.scene.collection.objects.link(obj)
    
    return imported_objects


def position_object(
    obj: bpy.types.Object,
    pos_x: float = 0.0,
    pos_y: float = 0.0,
    pos_z: float = 0.0,
) -> None:
    """Position an object at the specified location."""
    obj.location = (pos_x, pos_y, pos_z)


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


def find_armature(
    imported_objects: list[bpy.types.Object],
) -> Optional[bpy.types.Object]:
    """Find the armature object from imported objects."""
    for obj in imported_objects:
        if obj.type == "ARMATURE":
            return obj
    return None


def find_pointcloud(
    imported_objects: list[bpy.types.Object],
) -> Optional[bpy.types.Object]:
    """Find the Pointcloud object from imported objects."""
    for obj in imported_objects:
        if obj.name == "Pointcloud":
            return obj
    return None


@app.command()
def main(
    fbx: Annotated[
        str,
        typer.Option(
            "--fbx",
            help="Path to the FBX character file",
        ),
    ],
    pointcloud: Annotated[
        str,
        typer.Option(
            "--pointcloud",
            help="Path to the blend file containing the point cloud",
        ),
    ],
    char_x: Annotated[
        float,
        typer.Option(
            "--char-x",
            help="Character position X",
        ),
    ] = 0.0,
    char_y: Annotated[
        float,
        typer.Option(
            "--char-y",
            help="Character position Y",
        ),
    ] = 0.0,
    char_z: Annotated[
        float,
        typer.Option(
            "--char-z",
            help="Character position Z",
        ),
    ] = 0.0,
    char_rx: Annotated[
        float,
        typer.Option(
            "--char-rx",
            help="Character rotation around X axis (degrees)",
        ),
    ] = 0.0,
    char_ry: Annotated[
        float,
        typer.Option(
            "--char-ry",
            help="Character rotation around Y axis (degrees)",
        ),
    ] = 0.0,
    char_rz: Annotated[
        float,
        typer.Option(
            "--char-rz",
            help="Character rotation around Z axis (degrees)",
        ),
    ] = 0.0,
    output: Annotated[
        Optional[str],
        typer.Option(
            "--output",
            help="Output blend filename (default: character_pointcloud.blend)",
        ),
    ] = None,
) -> None:
    """Combine character FBX with point cloud blend file."""
    
    # Resolve paths
    fbx_path = Path(fbx).resolve()
    pointcloud_path = Path(pointcloud).resolve()
    
    # Determine output filename
    if output:
        output_path = Path(output).resolve()
    else:
        fbx_name = fbx_path.stem
        pc_name = pointcloud_path.stem
        output_path = Path.cwd() / f"{fbx_name}_{pc_name}.blend"
    
    typer.secho(f"Character + Point Cloud Combiner", fg=typer.colors.BLUE, bold=True)
    typer.secho(f"Character FBX: {fbx_path.name}", fg=typer.colors.CYAN)
    typer.secho(f"Point Cloud:   {pointcloud_path.name}", fg=typer.colors.CYAN)
    typer.secho(f"Output:        {output_path.name}", fg=typer.colors.CYAN)
    typer.echo("=" * 50)
    
    # Step 1: Reset scene
    typer.echo("1. Resetting scene...")
    reset_scene()
    
    # Step 2: Import point cloud (which already has RadianceField)
    typer.echo("2. Importing point cloud...")
    pc_objects = import_blend(pointcloud_path)
    pointcloud_obj = find_pointcloud(pc_objects)
    if pointcloud_obj:
        typer.secho(f"[+] Point cloud loaded: {pointcloud_obj.name}", fg=typer.colors.GREEN)
    else:
        typer.secho(f"Warning: Pointcloud object not found, but blend imported", fg=typer.colors.YELLOW)
    
    # Step 3: Import character FBX
    typer.echo("3. Importing character FBX...")
    char_objects = import_fbx(fbx_path)
    armature = find_armature(char_objects)
    if armature:
        typer.secho(f"[+] Character armature loaded: {armature.name}", fg=typer.colors.GREEN)
    else:
        typer.secho(f"Warning: No armature found in FBX", fg=typer.colors.YELLOW)
    
    # Step 4: Position and rotate character
    if armature:
        if char_x != 0 or char_y != 0 or char_z != 0:
            typer.echo("4. Positioning character...")
            position_object(armature, char_x, char_y, char_z)
            typer.secho(
                f"[+] Character positioned: X={char_x} Y={char_y} Z={char_z}",
                fg=typer.colors.GREEN,
            )
        else:
            typer.echo("4. No character position specified")
        
        if char_rx != 0 or char_ry != 0 or char_rz != 0:
            typer.echo("5. Rotating character...")
            rotate_object(armature, char_rx, char_ry, char_rz)
            typer.secho(
                f"[+] Character rotated: X={char_rx}° Y={char_ry}° Z={char_rz}°",
                fg=typer.colors.GREEN,
            )
        else:
            typer.echo("5. No character rotation specified")
    else:
        typer.echo("4-5. No character to position/rotate")
    
    # Step 6: Save combined blend file
    typer.echo("6. Saving combined blend file...")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(output_path))
    
    typer.secho(f"[+] Successfully saved: {output_path}", fg=typer.colors.GREEN)
    typer.secho(f"[+] Combined file contains:", fg=typer.colors.GREEN)
    if pointcloud_obj:
        typer.secho(f"    - Point cloud: {pointcloud_obj.name} (with RadianceField)", fg=typer.colors.CYAN)
    if armature:
        typer.secho(f"    - Character: {armature.name}", fg=typer.colors.CYAN)


if __name__ == "__main__":
    app()
