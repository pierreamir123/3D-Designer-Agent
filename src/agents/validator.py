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
        
        # Ensure outputs directory exists
        output_dir = os.path.join(os.getcwd(), "outputs")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        # Generate timestamped filename
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_stl = os.path.join(output_dir, f"design_{timestamp}.stl")
        
        # Prepend logic to force set filepath if the variable is used.
        # We use raw string for path to avoid escape issue on Windows
        script = f"output_path = r'{output_stl}'\n" + bpy_code
        
        result = BlenderOps.execute_bpy(script)
        
        if not result["success"]:
            logger.error(f"Execution Error: {result['error']}")
            current_retries = state.get("retry_count", 0)
            return {
                "errors": [result["error"]],
                "messages": state.get("messages", []) + [f"Validator found error: {result['error']}"],
                "retry_count": current_retries + 1
            }
            
        # Check if STL exists
        logger.info(f"BPY executed successfully. Validating mesh: {output_stl}")
        validation = BlenderOps.validate_stl(output_stl)
        if not validation["valid"]:
             logger.warning(f"Mesh Issues Found: {validation['issues']}")
             current_retries = state.get("retry_count", 0)
             return {
                "errors": validation["issues"],
                 "messages": state.get("messages", []) + [f"Validator found mesh issues: {validation['issues']}"],
                 "retry_count": current_retries + 1
             }
             
        logger.info("STL validation successful. Object is ready.")
        return {
            "stl_path": output_stl,
            "errors": []
        }
