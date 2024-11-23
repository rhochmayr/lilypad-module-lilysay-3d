import bpy
import sys
import math
from mathutils import Vector
from cowsay import cowsay

# Get arguments passed from the command line
argv = sys.argv
argv = argv[argv.index("--") + 1:]  # get all args after "--"

cow_type = argv[0]
message = argv[1]

print(f"cow_type: {cow_type }")  
print(f"message: {message }")  

# Function to delete all existing objects in the scene
def delete_all_objects():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

# Function to create and extrude text objects
def create_text_objects(ascii_art):
    text_objects = []
    # Set the spacing
    char_width = 0.8
    line_height = 1.2

    # Create text objects
    for y, line in enumerate(ascii_art):
        for x, char in enumerate(line):
            if char != ' ':
                # Create a text object
                bpy.ops.object.text_add(location=(0, 0, 0))
                text_obj = bpy.context.object
                text_obj.data.body = char

                # Extrude the text object
                text_obj.data.extrude = 0.1  # Adjust for better visibility

                # Add some bevel for better visibility
                text_obj.data.bevel_depth = 0.02
                text_obj.data.bevel_resolution = 3

                # Adjust the material
                material = bpy.data.materials.new(name=f"Material_{char}")
                material.use_nodes = True
                bsdf = material.node_tree.nodes.get("Principled BSDF")
                if bsdf:
                    bsdf.inputs['Base Color'].default_value = (0.8, 0.5, 0.1, 1)  # Orange color
                    bsdf.inputs['Roughness'].default_value = 0.5  # Matte finish
                    # bsdf.inputs['Specular'].default_value = 0.5  # Subtle shine
                text_obj.data.materials.append(material)

                # Adjust the location and rotation
                text_obj.location.x = 24.9  # Move to the right wall
                text_obj.location.y = 25 + x * -char_width  # Ensure it's flat on the wall and move along Y axis
                text_obj.location.z = len(ascii_art) * line_height - y * line_height  # Lift to the wall height
                text_obj.rotation_euler = (math.radians(90), 0, math.radians(-90))  # Rotate to align with the wall

                text_objects.append(text_obj)

    return text_objects

# Delete all existing objects
delete_all_objects()

# Create a seamless floor and backdrop with correct rotations and positions
# Floor plane
bpy.ops.mesh.primitive_plane_add(size=50, location=(0, 0, 0))
floor = bpy.context.object
floor_material = bpy.data.materials.new(name="FloorMaterial")
floor_material.use_nodes = True
bsdf = floor_material.node_tree.nodes.get("Principled BSDF")
if bsdf:
    bsdf.inputs['Base Color'].default_value = (0.8, 0.8, 0.8, 1)  # Light grey color
floor.data.materials.append(floor_material)

# Backdrop plane (right)
bpy.ops.mesh.primitive_plane_add(size=50, location=(25, 0, 25))
backdrop_right = bpy.context.object
backdrop_right.rotation_euler = (0, math.radians(90), 0)
backdrop_material = bpy.data.materials.new(name="BackdropMaterial")
backdrop_material.use_nodes = True
bsdf = backdrop_material.node_tree.nodes.get("Principled BSDF")
if bsdf:
    bsdf.inputs['Base Color'].default_value = (0.2, 0.6, 0.8, 1)  # Light blue color
backdrop_right.data.materials.append(backdrop_material)
bpy.ops.object.modifier_add(type='SOLIDIFY')
backdrop_right.modifiers["Solidify"].thickness = 0.1

# Backdrop plane (back)
bpy.ops.mesh.primitive_plane_add(size=50, location=(0, 25, 25))
backdrop_back = bpy.context.object
backdrop_back.rotation_euler = (math.radians(90), 0, 0)
backdrop_material = bpy.data.materials.new(name="BackdropMaterial")
backdrop_material.use_nodes = True
bsdf = backdrop_material.node_tree.nodes.get("Principled BSDF")
if bsdf:
    bsdf.inputs['Base Color'].default_value = (0.2, 0.6, 0.8, 1)  # Light blue color
backdrop_back.data.materials.append(backdrop_material)
bpy.ops.object.modifier_add(type='SOLIDIFY')
backdrop_back.modifiers["Solidify"].thickness = 0.1

# Define the ASCII art as a list of strings
#message = "Blender on Lilypad rocks!"
#cow_type = 'turtle'  # Replace 'tux' with any available cow type
cow_output  = cowsay(message, cow=cow_type)
print(f"{cow_output } \n")  

# Split the cowsay output into lines
ascii_art = cow_output.split('\n')
 
# Create the text objects and position them on the right wall
text_objects = create_text_objects(ascii_art)

# Set up the camera
camera_distance = 50

if "Camera" in bpy.data.objects:
    camera = bpy.data.objects["Camera"]
else:
    bpy.ops.object.camera_add()
    camera = bpy.context.active_object

camera.location = Vector((-35, -35, 25))
camera.rotation_euler = (math.radians(82), 0, math.radians(-52))
bpy.context.scene.camera = camera

# Set up the main light
if "Light" in bpy.data.objects:
    light = bpy.data.objects["Light"]
else:
    bpy.ops.object.light_add(type='AREA')
    light = bpy.context.active_object

light.location = (0, 0, 50)
light.data.energy = 2500
light.data.size = 50

# Add an additional point light for better illumination
bpy.ops.object.light_add(type='POINT', location=(12.5, 12.5, 17))
additional_light = bpy.context.object
additional_light.data.energy = 2500

# Set up render settings
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.device = 'GPU'
bpy.context.preferences.addons['cycles'].preferences.get_devices()
bpy.context.preferences.addons['cycles'].preferences.compute_device_type = 'CUDA'
bpy.context.scene.cycles.samples = 512  # Increased samples for better quality
bpy.context.scene.render.image_settings.file_format = 'PNG'
bpy.context.scene.render.filepath = f"/outputs/scene_setup_render_{cow_type}.png"

# Render the scene
bpy.ops.render.render(write_still=True)