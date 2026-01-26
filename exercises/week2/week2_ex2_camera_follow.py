"""Week 2 Exercise 2: camera follow automation with optional Armature target."""

import bpy
from mathutils import Vector
from pathlib import Path

SAVE_NAME = "week2ex2.blend"
FRAME_START = 1
FRAME_END = 180
STEP = 10
Y_OFFSET = -3.0
Z_OFFSET = 3.0
TARGET_ARMATURE_NAME = "Armature"
TARGET_BONE_NAME = "mixamorig:Hips"


class TargetAdapter:
    """Provides frame-evaluated world positions regardless of target type."""

    def __init__(self, obj: bpy.types.Object, bone_name: str | None = None) -> None:
        self.obj = obj
        self.bone_name = bone_name

    def world_location(self) -> Vector:
        if self.obj.type == "ARMATURE" and self.bone_name:
            bone = self.obj.pose.bones.get(self.bone_name)
            if bone:
                matrix = self.obj.matrix_world @ bone.matrix
                return matrix.translation
        return self.obj.matrix_world.translation


def reset_scene() -> None:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.scene.render.engine = "CYCLES"
    bpy.context.scene.frame_start = FRAME_START
    bpy.context.scene.frame_end = FRAME_END


def ensure_object_mode() -> None:
    if bpy.context.mode != "OBJECT":
        bpy.ops.object.mode_set(mode="OBJECT")


def clear_objects() -> None:
    ensure_object_mode()
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)


def build_proxy_target() -> TargetAdapter:
    bpy.ops.object.empty_add(type="ARROWS", location=(0.0, 0.0, 1.0))
    proxy = bpy.context.active_object
    proxy.name = "ProxyRig"
    proxy.animation_data_clear()
    beats = (
        (FRAME_START, Vector((0.0, 0.0, 1.0))),
        (60, Vector((1.0, 1.5, 1.0))),
        (120, Vector((2.5, 3.0, 1.0))),
        (FRAME_END, Vector((4.0, 4.5, 1.0))),
    )
    for frame, location in beats:
        proxy.location = location
        proxy.keyframe_insert(data_path="location", frame=frame)
    return TargetAdapter(proxy)


def get_target_adapter() -> TargetAdapter:
    armature = bpy.data.objects.get(TARGET_ARMATURE_NAME)
    if armature:
        print("Using existing Armature as target.")
        return TargetAdapter(armature, TARGET_BONE_NAME)
    print("Armature not found; generating proxy target.")
    return build_proxy_target()


def point_camera(camera: bpy.types.Object, target: Vector) -> None:
    direction = target - camera.location
    camera.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def setup_camera() -> bpy.types.Object:
    camera_data = bpy.data.cameras.new(name="FollowCam")
    camera = bpy.data.objects.new("FollowCam", camera_data)
    bpy.context.collection.objects.link(camera)
    bpy.context.scene.camera = camera
    return camera


def add_lights(target: TargetAdapter) -> None:
    sun_data = bpy.data.lights.new(name="FollowKey", type="SUN")
    sun = bpy.data.objects.new("FollowKey", sun_data)
    bpy.context.collection.objects.link(sun)
    sun.location = Vector((12.0, -10.0, 20.0))
    point_camera(sun, target.world_location())
    sun_data.energy = 5.0

    fill_data = bpy.data.lights.new(name="FollowFill", type="AREA")
    fill = bpy.data.objects.new("FollowFill", fill_data)
    bpy.context.collection.objects.link(fill)
    fill.location = Vector((-6.0, 4.0, 5.0))
    fill.rotation_euler = (0.0, 0.0, 1.0)
    fill_data.energy = 1200.0
    fill_data.shape = "RECTANGLE"
    fill_data.size = 5.0
    fill_data.size_y = 2.5


def bake_camera_animation(camera: bpy.types.Object, target: TargetAdapter) -> None:
    for frame in range(FRAME_START, FRAME_END + 1, STEP):
        bpy.context.scene.frame_set(frame)
        target_loc = target.world_location()
        camera.location = Vector(
            (target_loc.x, target_loc.y + Y_OFFSET, max(target_loc.z + Z_OFFSET, 0.5))
        )
        point_camera(camera, target_loc)
        camera.keyframe_insert(data_path="location", frame=frame)
        camera.keyframe_insert(data_path="rotation_euler", frame=frame)


def build_environment() -> None:
    bpy.ops.mesh.primitive_plane_add(size=60.0, location=(0.0, 0.0, 0.0))
    plane = bpy.context.active_object
    plane.name = "FollowFloor"
    mat = bpy.data.materials.new(name="FollowFloorMaterial")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs[0].default_value = (0.03, 0.03, 0.035, 1.0)
    plane.data.materials.append(mat)


def main() -> None:
    reset_scene()
    clear_objects()
    build_environment()
    target = get_target_adapter()
    add_lights(target)
    camera = setup_camera()
    bake_camera_animation(camera, target)
    bpy.ops.wm.save_as_mainfile(filepath=str(Path(__file__).with_name(SAVE_NAME)))
    print("Week 2 Exercise 2 saved; camera offsets baked every 10 frames.")


if __name__ == "__main__":
    main()
