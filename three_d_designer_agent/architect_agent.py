import os
from typing import Dict, Any, Optional
from .state import GraphState


def architect_node(state: GraphState) -> Dict[str, Any]:
    """
    Architect Agent: BPY Code Generator
    Converts the JSON blueprint into high-quality, parametric Blender Python code.
    """
    print("Architect Agent generating BPY code from blueprint...")
    
    try:
        if not state.blueprint_json:
            raise ValueError("No blueprint JSON available for code generation")
        
        bpy_script = generate_bpy_script(state.blueprint_json)
        
        return {
            **vars(state),
            "generated_bpy_script": bpy_script,
            "code_generation_error": None,
            "current_step": "architect_complete"
        }
    except Exception as e:
        return {
            **vars(state),
            "code_generation_error": str(e),
            "current_step": "architect_failed"
        }


def generate_bpy_script(blueprint: Dict[str, Any]) -> str:
    """
    Generate a complete Blender Python script from the blueprint JSON.
    """
    script_parts = [
        "# Generated Blender Python Script",
        "# Object Name: {object_name}".format(object_name=blueprint.get("object_name", "Unknown")),
        "# Description: {description}".format(description=blueprint.get("metadata", {}).get("description", "No description")),
        "",
        "import bpy",
        "import bmesh",
        "from mathutils import Vector",
        "import os",
        "",
        "# Clear existing mesh objects",
        "bpy.ops.object.select_all(action='SELECT')",
        "bpy.ops.object.delete(use_global=False)",
        "",
        "# Create collection for our generated objects",
        "collection_name = '{object_name}_Collection'".format(object_name=blueprint.get("object_name", "Generated").replace(" ", "_")),
        "if collection_name in bpy.data.collections:",
        "    bpy.data.collections.remove(bpy.data.collections[collection_name])",
        "new_collection = bpy.data.collections.new(name=collection_name)",
        "bpy.context.scene.collection.children.link(new_collection)",
        "",
    ]
    
    # Add variable definitions for dimensions
    script_parts.extend([
        "# Parametric Variables",
    ])
    
    element_vars = {}
    for i, element in enumerate(blueprint.get("elements", [])):
        element_id = element.get("id", f"element_{i}")
        element_vars[element_id] = f"obj_{i}"
        
        # Add parametric variables for each element's dimensions
        dims = element.get("dimensions", {})
        for dim_key, dim_value in dims.items():
            if isinstance(dim_value, (int, float)):
                script_parts.append(f"{element_id}_{dim_key} = {dim_value}")
    
    script_parts.append("")
    
    # Add object creation code
    for i, element in enumerate(blueprint.get("elements", [])):
        element_id = element.get("id", f"element_{i}")
        prim_type = element.get("primitive_type", "MESH_CUBE")
        dims = element.get("dimensions", {})
        transform = element.get("transform", {})
        location = transform.get("location", [0, 0, 0])
        rotation = transform.get("rotation", [0, 0, 0])  # in radians
        
        script_parts.extend([
            f"# Create {prim_type} - {element_id}",
            f"bpy.ops.mesh.primitive_{prim_type.lower()[5:]}_add(",  # Remove MESH_ prefix
        ])
        
        # Add dimensions based on primitive type
        if prim_type == "MESH_CUBE":
            script_parts.extend([
                f"    size={dims.get('x', 2.0)/2}",  # Blender uses half-size for cubes
                f"    location=({location[0]}, {location[1]}, {location[2]})",
                f"    rotation=({rotation[0]}, {rotation[1]}, {rotation[2]})",
            ])
        elif prim_type == "MESH_CYLINDER":
            script_parts.extend([
                f"    radius={dims.get('radius', 1.0)}",
                f"    depth={dims.get('depth', 2.0)}",
                f"    vertices={dims.get('vertices', 32)}",
                f"    location=({location[0]}, {location[1]}, {location[2]})",
                f"    rotation=({rotation[0]}, {rotation[1]}, {rotation[2]})",
            ])
        elif prim_type == "MESH_UVSPHERE":
            script_parts.extend([
                f"    radius={dims.get('radius', 1.0)}",
                f"    segments={dims.get('segments', 32)}",
                f"    ring_count={dims.get('ring_count', 16)}",
                f"    location=({location[0]}, {location[1]}, {location[2]})",
                f"    rotation=({rotation[0]}, {rotation[1]}, {rotation[2]})",
            ])
        elif prim_type == "MESH_CONE":
            script_parts.extend([
                f"    radius1={dims.get('radius1', 1.0)}",
                f"    radius2={dims.get('radius2', 0.0)}",
                f"    depth={dims.get('depth', 2.0)}",
                f"    vertices={dims.get('vertices', 32)}",
                f"    location=({location[0]}, {location[1]}, {location[2]})",
                f"    rotation=({rotation[0]}, {rotation[1]}, {rotation[2]})",
            ])
        elif prim_type == "MESH_TORUS":
            script_parts.extend([
                f"    major_radius={dims.get('major_radius', 1.0)}",
                f"    minor_radius={dims.get('minor_radius', 0.25)}",
                f"    major_segments={dims.get('major_segments', 48)}",
                f"    minor_segments={dims.get('minor_segments', 12)}",
                f"    location=({location[0]}, {location[1]}, {location[2]})",
                f"    rotation=({rotation[0]}, {rotation[1]}, {rotation[2]})",
            ])
        else:  # Default to cube
            script_parts.extend([
                f"    size=1.0",
                f"    location=({location[0]}, {location[1]}, {location[2]})",
                f"    rotation=({rotation[0]}, {rotation[1]}, {rotation[2]})",
            ])
        
        script_parts.extend([
            ")",
            f"current_obj = bpy.context.active_object",
            f"current_obj.name = '{element_id}'",
            f"new_collection.objects.link(current_obj)",
            "",
        ])
    
    # Add boolean operations to combine objects
    script_parts.extend([
        "# Apply Boolean Operations",
        "# First, make sure we have objects to work with",
        "all_objects = list(new_collection.objects)",
        "if len(all_objects) > 1:",
        "    # Start with the first object as the main body",
        "    main_obj = all_objects[0]",
        "    bpy.context.view_layer.objects.active = main_obj",
        "    main_obj.select_set(True)",
        "",
        "    # Process each element for boolean operations",
    ])
    
    for i, element in enumerate(blueprint.get("elements", [])[1:], 1):  # Skip first element
        element_id = element.get("id", f"element_{i}")
        boolean_op = element.get("boolean_op", "UNION")
        
        script_parts.extend([
            f"    # Process {element_id} with {boolean_op} operation",
            f"    tool_obj = bpy.data.objects.get('{element_id}')",
            f"    if tool_obj:",
            f"        # Add boolean modifier to main object",
            f"        bool_modifier = main_obj.modifiers.new(name='Boolean_{i}', type='BOOLEAN')",
            f"        bool_modifier.operation = '{boolean_op.upper()}'",
            f"        bool_modifier.object = tool_obj",
            f"        # Hide the tool object",
            f"        tool_obj.hide_viewport = True",
            f"        tool_obj.hide_render = True",
            "",
        ])
    
    # Add final cleanup and selection
    script_parts.extend([
        "# Make the main object active and selected",
        "if all_objects:",
        "    main_obj = all_objects[0]",
        "    bpy.context.view_layer.objects.active = main_obj",
        "    for obj in all_objects:",
        "        obj.select_set(True)",
        "",
        "# Export as STL",
        "output_dir = bpy.context.preferences.filepaths.render_output_directory or './'",
        "output_path = os.path.join(output_dir, '{}.stl')".format(blueprint.get("object_name", "generated_object")),
        "try:",
        "    bpy.ops.export_mesh.stl(filepath=output_path, use_selection=True)",
        "    print(f'Exported STL to: {{output_path}}')",
        "except Exception as e:",
        "    print(f'Export failed: {{e}}')",
        "",
        "# Report final object count",
        "print(f'Generated {{len(all_objects)}} objects')",
    ])
    
    return "\n".join(script_parts)