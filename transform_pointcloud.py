"""Transform point cloud: rotate 90 degrees on X axis and freeze transforms.

Usage:
    python transform_pointcloud.py --input pointclouds/Mailbox_point_cloud.blend [--output OUTPUT.blend]
"""

from pathlib import Path
from typing import Optional

import bpy
import typer
from typing_extensions import Annotated

app = typer.Typer(help="Transform point cloud and freeze transforms")


@app.command()
def main(
    input_file: Annotated[
        str,
        typer.Option(
            "--input",
            help="Path to the input blend file with point cloud",
        ),
    ],
    output: Annotated[
        Optional[str],
        typer.Option(
            "--output",
            help="Output blend filename (default: same as input)",
        ),
    ] = None,
) -> None:
    """Load a blend file, rotate point cloud 90° on X axis, freeze transforms, and export."""
    
    # Resolve paths
    input_path = Path(input_file).resolve()
    
    if not input_path.exists():
        typer.secho(f"Error: Input file not found: {input_path}", fg=typer.colors.RED)
        raise typer.Exit(code=1)
    
    # Determine output filename
    if output:
        output_path = Path(output).resolve()
    else:
        output_path = input_path
    
    typer.secho(f"Point cloud transformation tool", fg=typer.colors.BLUE, bold=True)
    typer.secho(f"Input:  {input_path}", fg=typer.colors.CYAN)
    typer.secho(f"Output: {output_path}", fg=typer.colors.CYAN)
    
    # Open the blend file
    typer.echo("Opening blend file...")
    bpy.ops.wm.open_mainfile(filepath=str(input_path))
    
    # Find the Pointcloud object
    typer.echo("Finding Pointcloud object...")
    if "Pointcloud" not in bpy.data.objects:
        typer.secho("Error: 'Pointcloud' object not found in blend file", fg=typer.colors.RED)
        raise typer.Exit(code=1)
    
    pointcloud = bpy.data.objects["Pointcloud"]
    typer.secho(f"[+] Found Pointcloud: {pointcloud.name}", fg=typer.colors.GREEN)
    
    # Set object as active and select it
    bpy.context.view_layer.objects.active = pointcloud
    pointcloud.select_set(True)
    
    # Rotate 90 degrees on X axis
    import math
    typer.echo("Rotating 90 degrees on X axis...")
    pointcloud.rotation_euler.x = math.radians(90)
    typer.secho(f"[+] Rotated on X axis: 90°", fg=typer.colors.GREEN)
    
    # Freeze transforms (apply transforms)
    typer.echo("Freezing transforms...")
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
    typer.secho(f"[+] Transforms frozen (applied)", fg=typer.colors.GREEN)
    
    # Verify the rotation was applied
    typer.echo(f"Pointcloud rotation after freezing: {pointcloud.rotation_euler}")
    typer.echo(f"Pointcloud location: {pointcloud.location}")
    
    # Save the blend file
    typer.echo(f"Saving blend file: {output_path.name}")
    bpy.ops.wm.save_as_mainfile(filepath=str(output_path))
    
    typer.secho(f"[+] Successfully saved: {output_path}", fg=typer.colors.GREEN)
    typer.secho(f"[+] Point cloud rotated 90° on X axis and transforms frozen", fg=typer.colors.GREEN)


if __name__ == "__main__":
    app()
