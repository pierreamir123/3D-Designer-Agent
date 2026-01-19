import contextlib
import traceback
from src.config.logger import get_logger

logger = get_logger("BlenderOps")

class BlenderOps:
    @staticmethod
    def execute_bpy(script_content: str) -> dict:
        """
        Executes the provided BPY script content in a separate subprocess.
        Includes automated mesh quality analysis.
        """
        import subprocess
        import tempfile
        import os
        import sys
        import json

        logger.info("Executing BPY script (Isolated Mode)...")
        
        # We inject a helper at the end to check all meshes
        analysis_helper = """
import json
import bmesh
results = []
for obj in bpy.data.objects:
    if obj.type == 'MESH':
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        issues = []
        if any(not e.is_manifold for e in bm.edges):
            issues.append("Non-manifold geometry detected")
        if any(f.calc_area() <= 0 for f in bm.faces):
            issues.append("Degenerate faces found")
        bm.free()
        results.append({"name": obj.name, "issues": issues})
print("---MESH_ANALYSIS_START---")
print(json.dumps(results))
print("---MESH_ANALYSIS_END---")
"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as tf:
            full_script = "import bpy\nimport math\n"
            full_script += "try:\n    bpy.ops.wm.read_factory_settings(use_empty=True)\nexcept: pass\n\n"
            full_script += script_content
            full_script += analysis_helper
            tf.write(full_script)
            temp_path = tf.name

        try:
            result = subprocess.run(
                [sys.executable, temp_path],
                capture_output=True,
                text=True,
                encoding='utf-8',
                timeout=30
            )
            
            stdout = result.stdout
            stderr = result.stderr
            
            # Parse mesh analysis
            mesh_issues = []
            if "---MESH_ANALYSIS_START---" in stdout:
                try:
                    analysis_block = stdout.split("---MESH_ANALYSIS_START---")[1].split("---MESH_ANALYSIS_END---")[0].strip()
                    mesh_info = json.loads(analysis_block)
                    for info in mesh_info:
                        if info["issues"]:
                            mesh_issues.extend([f"[{info['name']}] {i}" for i in info["issues"]])
                except:
                    pass

            if result.returncode != 0:
                err_msg = f"BPY Subprocess failed ({result.returncode}).\nStderr: {stderr}"
                return {"success": False, "error": err_msg, "stdout": stdout, "mesh_issues": mesh_issues}
                
            return {"success": True, "error": None, "stdout": stdout, "mesh_issues": mesh_issues}
        except Exception as e:
            return {"success": False, "error": str(e), "stdout": "", "mesh_issues": []}
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    @staticmethod
    def validate_stl(file_path: str) -> dict:
        logger.info(f"Validating STL file: {file_path}")
        import os
        if not os.path.exists(file_path):
            return {"valid": False, "issues": ["STL file was not created"]}
            
        size = os.path.getsize(file_path)
        if size < 100:
             return {"valid": False, "issues": [f"STL file is too small ({size} bytes), likely empty"]}
             
        logger.info(f"STL basic validation passed: {size} bytes.")
        return {"valid": True, "issues": []}
