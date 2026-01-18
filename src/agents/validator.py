from src.state import GraphState
from src.utils.blender_ops import BlenderOps
import os

class ValidatorAgent:
    def __init__(self):
        pass

    def run(self, state: GraphState):
        bpy_code = state.get("bpy_code", "")
        # Ensure export path is set in the code or injected
        # The Architect agent was instructed to use 'output_path' or include export logic.
        # We can inject a specific path variable if needed, or rely on the code.
        # Let's simple check if "filepath=" is in the code, or prepend a variable definition.
        
        output_stl = os.path.abspath("output.stl")
        
        # Inject output_path if not present (simple heuristic)
        # We'll prepend it to make sure the script has access to 'output_path' if it uses it.
        # If the architect wrote `output_path = ...` itself, this might conflict, but usually safe to set var.
        # Better: Architect instructions said "filepath=...". We should probably inject the export command if missing, 
        # or rewrite the filepath.
        # Let's just create a temporary file path and replace 'output.stl' or similar if found, 
        # or better, simply prepending `output_path = r'...'` and hoping the LLM used it or hardcoded something we can't easily change without parsing.
        
        # Strategy: The Architect prompt said "include a final block... stl_export(filepath=...)". 
        # We will try to let it run. But we need to know WHERE it saved it.
        # For this demo, let's enforce a specific path by replacing likely placeholders or just hoping the LLM creates 'output.stl'.
        # We will wrap the execution to try to find the latest STL or just use a fixed one.
        
        # Hack for consistency:
        # Prepend logic to force set filepath if the variable is used.
        script = f"output_path = r'{output_stl}'\n" + bpy_code
        
        result = BlenderOps.execute_bpy(script)
        
        if not result["success"]:
            return {
                "errors": [result["error"]],
                "messages": state.get("messages", []) + [f"Validator found error: {result['error']}"]
            }
            
        # Check if STL exists
        validation = BlenderOps.validate_stl(output_stl)
        if not validation["valid"]:
             return {
                "errors": validation["issues"],
                 "messages": state.get("messages", []) + [f"Validator found mesh issues: {validation['issues']}"]
             }
             
        return {
            "stl_path": output_stl,
            "errors": []
        }
