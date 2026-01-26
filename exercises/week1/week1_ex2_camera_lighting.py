"""Week 1 Exercise 2: build a procedural camera + lighting rig and render a still."""

import bpy
from mathutils import Vector
from pathlib import Path

SAVE_NAME = "week1ex2.blend"
STILL_NAME = "week1ex2.png"


def reset_scene() -> None:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.scene.render.engine = "CYCLES"
    bpy.context.scene.render.resolution_x = 1920
    bpy.context.scene.render.resolution_y = 1080
    bpy.context.scene.render.image_settings.file_format = "PNG"


def ensure_object_mode() -> None:
    if bpy.context.mode != "OBJECT":
        bpy.ops.object.mode_set(mode="OBJECT")


def clear_objects() -> None:
    ensure_object_mode()
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)


def add_floor() -> bpy.types.Object:
    bpy.ops.mesh.primitive_plane_add(size=25.0, location=(0.0, 0.0, -1.5))
    plane = bpy.context.active_object
    mat = bpy.data.materials.new(name="Floor")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs[0].default_value = (0.07, 0.07, 0.07, 1.0)
    bsdf.inputs[7].default_value = 0.8  # roughness
    plane.data.materials.append(mat)
    return plane


def add_hero_object() -> bpy.types.Object:
    bpy.ops.mesh.primitive_monkey_add(size=1.5, location=(0.0, 0.0, 0.0))
    obj = bpy.context.active_object
    obj.name = "HeroSuzanne"
    mat = bpy.data.materials.new(name="Hero")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs[0].default_value = (0.85, 0.5, 0.1, 1.0)
    bsdf.inputs[5].default_value = 0.4  # metallic
    obj.data.materials.append(mat)
    bpy.ops.object.shade_smooth()
    return obj


def aim_at(obj: bpy.types.Object, target: Vector) -> None:
    direction = target - obj.location
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def add_camera(target: Vector) -> bpy.types.Object:
    camera_data = bpy.data.cameras.new(name="TD_Camera")
    camera_object = bpy.data.objects.new("TD_Camera", camera_data)
    bpy.context.collection.objects.link(camera_object)
    camera_object.location = Vector((8.0, -8.0, 6.0))
    aim_at(camera_object, target)
    bpy.context.scene.camera = camera_object
    return camera_object


def add_lights(target: Vector) -> None:
    sun_data = bpy.data.lights.new(name="KeySun", type="SUN")
    sun = bpy.data.objects.new("KeySun", sun_data)
    bpy.context.collection.objects.link(sun)
    sun.location = Vector((12.0, -6.0, 15.0))
    aim_at(sun, target)
    sun_data.energy = 2.5

    fill_data = bpy.data.lights.new(name="FillLight", type="AREA")
    fill = bpy.data.objects.new("FillLight", fill_data)
    bpy.context.collection.objects.link(fill)
    fill.location = Vector((-6.0, 4.0, 5.0))
    fill.rotation_euler = (0.0, 0.0, 0.6)
    fill_data.energy = 600.0
    fill_data.shape = "RECTANGLE"
    fill_data.size = 4.0
    fill_data.size_y = 2.0


def render_still(output_path: Path) -> None:
    bpy.context.scene.frame_set(1)
    bpy.context.scene.render.filepath = str(output_path)
    bpy.ops.render.render(write_still=True)


def main() -> None:
    reset_scene()
    clear_objects()
    add_floor()
    hero = add_hero_object()
    add_camera(hero.location)
    add_lights(hero.location)
    render_still(Path(__file__).with_name(STILL_NAME))
    bpy.ops.wm.save_as_mainfile(filepath=str(Path(__file__).with_name(SAVE_NAME)))
    print("Week 1 Exercise 2 complete")


if __name__ == "__main__":
    main()
