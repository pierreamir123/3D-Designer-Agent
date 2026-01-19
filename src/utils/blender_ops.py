import contextlib
import traceback
from src.config.logger import get_logger

logger = get_logger("BlenderOps")

class BlenderOps:
    @staticmethod
    def execute_bpy(script_content: str, execution_mode="exec") -> dict:
        """
        Executes the provided BPY script content.
        """
        logger.info("Executing BPY script...")
        try:
            import bpy
            import math
            # We might want to clear the scene first
            bpy.ops.wm.read_factory_settings(use_empty=True)
        except ImportError:
            msg = "The 'bpy' module is not installed. Please install it via 'pip install bpy' or run in Blender."
            logger.error(msg)
            return {
                "success": False, 
                "error": msg,
                "stdout": ""
            }

        # Capture stdout/stderr
        import io
        output_buffer = io.StringIO()
        
        try:
            with contextlib.redirect_stdout(output_buffer), contextlib.redirect_stderr(output_buffer):
                # We need to execute the script in a namespace that has bpy
                exec_globals = {"bpy": bpy, "math": math}
                exec(script_content, exec_globals)
        except Exception:
            err_msg = traceback.format_exc()
            logger.error(f"Error during BPY execution:\n{err_msg}")
            return {
                "success": False,
                "error": err_msg,
                "stdout": output_buffer.getvalue()
            }
            
        logger.info("BPY execution successful.")
        return {
            "success": True, 
            "error": None, 
            "stdout": output_buffer.getvalue()
        }

    @staticmethod
    def validate_stl(file_path: str) -> dict:
        logger.info(f"Validating STL file: {file_path}")
        import os
        if os.path.exists(file_path) and os.path.getsize(file_path) > 100:
             logger.info(f"STL validation passed: {os.path.getsize(file_path)} bytes.")
             return {"valid": True, "issues": []}
        
        issues = ["File not created or empty"]
        logger.warning(f"STL validation failed: {issues}")
        return {"valid": False, "issues": issues}
