from src.state import GraphState
from src.utils.blender_ops import BlenderOps
from src.config.logger import get_logger
import os

logger = get_logger("Validator")

class ValidatorAgent:
    def __init__(self):
        pass

    def run(self, state: GraphState):
        bpy_code = state.get("bpy_code", "")
        logger.info("Executing BPY script and checking for STL generation...")
        
        output_stl = os.path.abspath("output.stl")
        
        # Prepend logic to force set filepath if the variable is used.
        script = f"output_path = r'{output_stl}'\n" + bpy_code
        
        result = BlenderOps.execute_bpy(script)
        
        if not result["success"]:
            logger.error(f"Execution Error: {result['error']}")
            return {
                "errors": [result["error"]],
                "messages": state.get("messages", []) + [f"Validator found error: {result['error']}"]
            }
            
        # Check if STL exists
        logger.info(f"BPY executed successfully. Validating mesh: {output_stl}")
        validation = BlenderOps.validate_stl(output_stl)
        if not validation["valid"]:
             logger.warning(f"Mesh Issues Found: {validation['issues']}")
             return {
                "errors": validation["issues"],
                 "messages": state.get("messages", []) + [f"Validator found mesh issues: {validation['issues']}"]
             }
             
        logger.info("STL validation successful. Object is ready.")
        return {
            "stl_path": output_stl,
            "errors": []
        }
