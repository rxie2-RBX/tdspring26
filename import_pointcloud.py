"""Import point cloud PLY file and save as Blender blend file.

Usage:
    python import_pointcloud.py --ply-file pointclouds/Mailbox_point_cloud.ply [--radiance] [--output OUTPUT.blend]
"""

from pathlib import Path
from typing import Optional

import bpy
import typer
from typing_extensions import Annotated

app = typer.Typer(help="Import point cloud PLY and save as blend file")


def reset_scene() -> None:
    """Reset to a clean scene with proper settings."""
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.scene.render.engine = "CYCLES"
    
    # Standard viewport settings
    bpy.context.scene.render.resolution_x = 1920
    bpy.context.scene.render.resolution_y = 1080
    bpy.context.scene.render.resolution_percentage = 100


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

    # Name the first object "Pointcloud"
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
            typer.secho(f"    [*] Point cloud has isolated vertices (no faces)", fg=typer.colors.CYAN)
    
    return pointcloud


def apply_material_to_object(
    obj: bpy.types.Object,
    material_name: str = "PointcloudMaterial",
) -> None:
    """Apply a bright white material to visualize the point cloud."""
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


def load_nodgroup_from_blend(blend_file: Path, node_group_name: str) -> bool:
    """Load a node group from an external blend file."""
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


def apply_geometry_nodes_to_pointcloud(
    pointcloud: bpy.types.Object,
    node_group_name: str = "RadianceField",
) -> bool:
    """Apply a geometry node group to the pointcloud object."""
    try:
        # Check if the node group exists by name
        node_group = bpy.data.node_groups[node_group_name]
        
        # Add RadianceField modifier
        geo_mod = pointcloud.modifiers.new(name="RadianceField", type="NODES")
        geo_mod.node_group = node_group
        
        typer.secho(
            f"[+] Applied geometry node group: {node_group_name}",
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


@app.command()
def main(
    ply_file: Annotated[
        str,
        typer.Option(
            "--ply-file",
            help="Path to the PLY point cloud file (relative to workspace root)",
        ),
    ],
    radiance: Annotated[
        bool,
        typer.Option(
            "--radiance",
            help="Apply RadianceField geometry nodes (requires radiancefield.blend)",
        ),
    ] = False,
    radiance_path: Annotated[
        Optional[str],
        typer.Option(
            "--radiance-path",
            help="Path to radiancefield.blend (default: exercises/project2/radiancefield.blend)",
        ),
    ] = None,
    output: Annotated[
        Optional[str],
        typer.Option(
            "--output",
            help="Output blend filename (default: Mailbox_point_cloud.blend)",
        ),
    ] = None,
) -> None:
    """Import a point cloud PLY file and save as a Blender blend file."""
    
    # Resolve paths
    ply_path = Path(ply_file).resolve()
    
    if radiance_path:
        radiancefield_path = Path(radiance_path).resolve()
    else:
        radiancefield_path = Path("exercises/project2/radiancefield.blend").resolve()
    
    # Determine output filename
    if output:
        output_path = Path(output)
    else:
        # Use PLY filename as base for output blend file
        output_path = ply_path.parent / f"{ply_path.stem}.blend"
    
    typer.secho(f"Point cloud import tool", fg=typer.colors.BLUE, bold=True)
    typer.secho(f"PLY file: {ply_path}", fg=typer.colors.CYAN)
    typer.secho(f"Output: {output_path}", fg=typer.colors.CYAN)
    
    # Reset scene
    typer.echo("Resetting Blender scene...")
    reset_scene()
    
    # Import PLY
    pointcloud = import_ply(ply_path)
    if not pointcloud:
        typer.secho("Error: Failed to import point cloud", fg=typer.colors.RED)
        raise typer.Exit(code=1)
    
    # Apply material
    apply_material_to_object(pointcloud)
    
    # Apply RadianceField if requested
    if radiance:
        typer.echo("Loading RadianceField geometry nodes...")
        if load_nodgroup_from_blend(radiancefield_path, "RadianceField"):
            apply_geometry_nodes_to_pointcloud(pointcloud, "RadianceField")
        else:
            typer.secho(
                "Warning: Could not apply RadianceField (continuing without it)",
                fg=typer.colors.YELLOW,
            )
    
    # Save blend file
    typer.echo(f"Saving blend file: {output_path.name}")
    bpy.ops.wm.save_as_mainfile(filepath=str(output_path))
    
    typer.secho(f"[+] Successfully saved: {output_path}", fg=typer.colors.GREEN)
    typer.secho(f"[+] Point cloud vertices: {len(pointcloud.data.vertices)}", fg=typer.colors.GREEN)


if __name__ == "__main__":
    app()
