from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from src.state import GraphState
from src.config import config
from src.config.logger import get_logger
import json

logger = get_logger("Architect")

class ArchitectAgent:
    def __init__(self, model_name=None):
        # Use LiteLLM configuration
        llm_config = config.get_openai_config()
        if model_name:
            llm_config["model"] = model_name
        self.llm = ChatOpenAI(**llm_config)
        self.system_prompt = """You are the **BPY Code Architect**, a senior software engineer specialized in the Blender Python API.
**Coding Standards:**
1. **Parametric Logic:** Use variables for all dimensions and transforms to allow for non-destructive editing.
2. **Library Usage:** Use `bpy.ops` for object creation and `bpy.data` for precise attribute manipulation.
3. **Printability:** Ensure all primitive intersections use Boolean Modifiers to create a single 'watertight' and 'manifold' mesh suitable for STL export. 
4. **Export Logic:** Always include a final block of code that ensures all created objects are selected and visible. Then export using a robust method that handles different Blender versions:
   ```python
   # Select all objects to ensure they are exported
   bpy.ops.object.select_all(action='SELECT')
   
   # Export logic (handles newer Blender 4.0+ and older versions)
   try:
       bpy.ops.wm.stl_export(filepath=output_path)
   except AttributeError:
       bpy.ops.export_mesh.stl(filepath=output_path)
   ```
   - The variable `output_path` will be injected into your script's local namespace.
   - IMPORANT: Start the script with `import bpy` and `import math`.
   - IMPORTANT: Clear existing usage with `bpy.ops.wm.read_factory_settings(use_empty=True)` at the very start.

"""

    def run(self, state: GraphState):
        blueprint = state["json_blueprint"]
        errors = state.get("errors", [])
        
        logger.info("Synthesizing BPY code from blueprint...")
        
        # Base Prompt
        msg_content = f"Generate BPY code for this blueprint:\n{json.dumps(blueprint, indent=2)}"
        
        # CONTEXT INJECTION: Feedback & Errors
        if state.get("feedback"):
             logger.info(f"Applying feedback: {state['feedback']}")
             msg_content += f"\n\nContext/User Feedback: {state['feedback']}"

        if errors:
            logger.info(f"Self-Correction Mode: Fixing {len(errors)} errors.")
            msg_content += f"\n\nCRITICAL: The previous code failed with the following errors. You MUST fix them:\n" + "\n".join(errors)

        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=msg_content)
        ]
        
        response = self.llm.invoke(messages)
        
        code = response.content
        # Extract code from markdown
        if "```python" in code:
            code = code.split("```python")[1].split("```")[0].strip()
        elif "```" in code:
            code = code.split("```")[1].split("```")[0].strip()
            
        logger.info(f"BPY script generated ({len(code)} characters).")
        return {"bpy_code": code}
