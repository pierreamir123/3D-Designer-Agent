import sys
import io
import contextlib
import traceback

class BlenderOps:
    @staticmethod
    def execute_bpy(script_content: str, execution_mode="exec") -> dict:
        """
        Executes the provided BPY script content.
        For now, we attempt to run it within the current python process assuming 'bpy' is installed.
        If 'bpy' is not installed, we return an error indicating dependency missing.
        
        Args:
            script_content (str): The python code to run.
            execution_mode (str): 'exec' (in-process) or 'subprocess' (TODO)
            
        Returns:
            dict: {"success": bool, "error": str, "stdout": str}
        """
        try:
            import bpy
            import math
            # We might want to clear the scene first
            bpy.ops.wm.read_factory_settings(use_empty=True)
        except ImportError:
            return {
                "success": False, 
                "error": "The 'bpy' module is not installed. Please install it via 'pip install bpy' (limited support) or run this agent within a Blender environment.",
                "stdout": ""
            }

        # Capture stdout/stderr
        output_buffer = io.StringIO()
        
        try:
            with contextlib.redirect_stdout(output_buffer), contextlib.redirect_stderr(output_buffer):
                # We need to execute the script in a namespace that has bpy
                exec_globals = {"bpy": bpy, "math": math}
                exec(script_content, exec_globals)
        except Exception:
            return {
                "success": False,
                "error": traceback.format_exc(),
                "stdout": output_buffer.getvalue()
            }
            
        return {
            "success": True, 
            "error": None, 
            "stdout": output_buffer.getvalue()
        }

    @staticmethod
    def validate_stl(file_path: str) -> dict:
        # In a real scenario, we'd use trimesh or blender to check manifoldness
        # For this MVP, we just check if file exists and has size > 0
        import os
        if os.path.exists(file_path) and os.path.getsize(file_path) > 100:
             return {"valid": True, "issues": []}
        return {"valid": False, "issues": ["File not created or empty"]}
