from src.state import GraphState
from src.utils.blender_ops import BlenderOps
import os

class ValidatorAgent:
    def __init__(self):
        pass

    def run(self, state: GraphState):
        bpy_code = state.get("bpy_code", "")
        print(f"   [Validator] Executing BPY script and checking for STL generation...")
        
        output_stl = os.path.abspath("output.stl")
        
        # Prepend logic to force set filepath if the variable is used.
        script = f"output_path = r'{output_stl}'\n" + bpy_code
        
        result = BlenderOps.execute_bpy(script)
        
        if not result["success"]:
            print(f"   [Validator] Execution Error: {result['error']}")
            return {
                "errors": [result["error"]],
                "messages": state.get("messages", []) + [f"Validator found error: {result['error']}"]
            }
            
        # Check if STL exists
        print(f"   [Validator] BPY executed successfully. Validating mesh: {output_stl}")
        validation = BlenderOps.validate_stl(output_stl)
        if not validation["valid"]:
             print(f"   [Validator] Mesh Issues Found: {validation['issues']}")
             return {
                "errors": validation["issues"],
                 "messages": state.get("messages", []) + [f"Validator found mesh issues: {validation['issues']}"]
             }
             
        print("   [Validator] STL validation successful. Object is ready.")
        return {
            "stl_path": output_stl,
            "errors": []
        }
