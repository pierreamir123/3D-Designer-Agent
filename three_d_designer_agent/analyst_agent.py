import json
import re
from typing import Dict, Any, Optional
from .state import GraphState


def analyst_node(state: GraphState) -> Dict[str, Any]:
    """
    Analyst Agent: Visual Decomposition Specialist
    Analyzes 2D images/text and outputs a structured JSON blueprint of geometric primitives.
    """
    print(f"Analyst Agent processing input: {state.user_input[:100]}...")
    
    # In a real implementation, this would use computer vision/image analysis
    # For now, we'll simulate based on text descriptions
    try:
        # Simple parsing logic to extract 3D elements from text description
        blueprint = parse_description_to_blueprint(state.user_input)
        
        return {
            **vars(state),
            "blueprint_json": blueprint,
            "analysis_error": None,
            "current_step": "analysis_complete"
        }
    except Exception as e:
        return {
            **vars(state),
            "analysis_error": str(e),
            "current_step": "analysis_failed"
        }


def parse_description_to_blueprint(description: str) -> Dict[str, Any]:
    """
    Parse a text description to generate a blueprint JSON.
    This is a simplified version - in reality, this would involve image analysis.
    """
    # Normalize the description
    desc_lower = description.lower()
    
    blueprint_elements = []
    
    # Look for basic shapes in the description
    if "cube" in desc_lower or "box" in desc_lower or "rectangular" in desc_lower:
        blueprint_elements.append({
            "id": "main_body",
            "primitive_type": "MESH_CUBE",
            "dimensions": {"x": 2.0, "y": 2.0, "z": 1.0},
            "transform": {"location": [0, 0, 0], "rotation": [0, 0, 0]},
            "boolean_op": "UNION"
        })
    
    if "cylinder" in desc_lower or "tube" in desc_lower or "pipe" in desc_lower:
        blueprint_elements.append({
            "id": "cylinder_feature",
            "primitive_type": "MESH_CYLINDER",
            "dimensions": {"radius": 0.5, "depth": 2.0, "vertices": 32},
            "transform": {"location": [1.5, 0, 0.5], "rotation": [0, 0, 0]},
            "boolean_op": "UNION"
        })
    
    if "sphere" in desc_lower or "ball" in desc_lower:
        blueprint_elements.append({
            "id": "spherical_feature",
            "primitive_type": "MESH_UVSPHERE",
            "dimensions": {"radius": 0.8, "segments": 32, "ring_count": 16},
            "transform": {"location": [-1.5, 0, 1.0], "rotation": [0, 0, 0]},
            "boolean_op": "UNION"
        })
    
    if "cone" in desc_lower:
        blueprint_elements.append({
            "id": "conical_feature",
            "primitive_type": "MESH_CONE",
            "dimensions": {"radius1": 0.8, "radius2": 0.1, "depth": 1.5, "vertices": 32},
            "transform": {"location": [0, 1.5, 0.75], "rotation": [0, 0, 0]},
            "boolean_op": "UNION"
        })
    
    if "torus" in desc_lower or "donut" in desc_lower:
        blueprint_elements.append({
            "id": "toroidal_feature",
            "primitive_type": "MESH_TORUS",
            "dimensions": {"major_radius": 1.0, "minor_radius": 0.3, "major_segments": 48, "minor_segments": 12},
            "transform": {"location": [0, -1.5, 1.0], "rotation": [1.5708, 0, 0]},  # Pi/2 radians = 90 degrees
            "boolean_op": "UNION"
        })
    
    # If no specific shapes were mentioned, create a simple default cube
    if not blueprint_elements:
        blueprint_elements.append({
            "id": "default_shape",
            "primitive_type": "MESH_CUBE",
            "dimensions": {"x": 2.0, "y": 2.0, "z": 2.0},
            "transform": {"location": [0, 0, 1], "rotation": [0, 0, 0]},
            "boolean_op": "UNION"
        })
    
    # Add some detail features based on other keywords
    if "hole" in desc_lower or "cutout" in desc_lower:
        blueprint_elements.append({
            "id": "cutout_cylinder",
            "primitive_type": "MESH_CYLINDER",
            "dimensions": {"radius": 0.3, "depth": 3.0, "vertices": 32},
            "transform": {"location": [0, 0, 1], "rotation": [0, 0, 0]},
            "boolean_op": "DIFFERENCE"  # This will cut through the main object
        })
    
    if "rounded" in desc_lower or "smooth" in desc_lower:
        # Add a small sphere to demonstrate boolean operations
        blueprint_elements.append({
            "id": "rounding_sphere",
            "primitive_type": "MESH_UVSPHERE",
            "dimensions": {"radius": 0.5, "segments": 32, "ring_count": 16},
            "transform": {"location": [0.8, 0.8, 1.8], "rotation": [0, 0, 0]},
            "boolean_op": "UNION"
        })
    
    return {
        "object_name": "Generated Object",
        "elements": blueprint_elements,
        "metadata": {
            "description": description,
            "element_count": len(blueprint_elements),
            "generated_by": "Analyst Agent"
        }
    }