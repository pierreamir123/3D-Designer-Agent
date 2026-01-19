from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from src.state import GraphState
from src.config import config
from src.config.logger import get_logger

logger = get_logger("Coder")

class CoderAgent:
    def __init__(self, model_name=None):
        # Use LiteLLM configuration
        llm_config = config.get_openai_config()
        if model_name:
            llm_config["model"] = model_name
        self.llm = ChatOpenAI(**llm_config)
        self.system_prompt = """You are the **BPY Scripting Expert**.
**Task:**
Generate a complete, runnable Blender Python (BPY) script based on the user's request.
**Rules:**
1.  **Direct Generation**: Do not create blueprints. Write the code directly.
2.  **Runnable**: The script must be executable in Blender 4.x.
3.  **Imports**: Always start with `import bpy` and `import math`.
4.  **Cleanup**: Always include `bpy.ops.wm.read_factory_settings(use_empty=True)` at the start to clear the scene.
5.  **Export Logic**: Always include a final block to select all objects and export to STL. Use the variable `output_path` which will be injected.
    ```python
    # ... code ...
    bpy.ops.object.select_all(action='SELECT')
    try:
        bpy.ops.wm.stl_export(filepath=output_path)
    except AttributeError:
        bpy.ops.export_mesh.stl(filepath=output_path)
    ```

**Output:**
Return ONLY the Python code, wrapped in ```python ... ``` blocks.
"""

    def run(self, state: GraphState):
        input_data = state.get("input_data", "No input provided")
        logger.info(f"Generating script for: {input_data[:50]}...")
        messages = [SystemMessage(content=self.system_prompt)]
        
        # Add User input
        messages.append(HumanMessage(content=f"Write a Blender script to: {input_data}"))
        
        # Handle Feedback/Correction from Validator
        errors = state.get("errors", [])
        if errors:
            logger.info(f"Self-Correction: Fixing {len(errors)} errors.")
            messages.append(HumanMessage(content=f"Previous attempt failed with errors:\n" + "\n".join(errors) + "\nPlease fix the script."))

        response = self.llm.invoke(messages)
        content = response.content
        
        # Extract code
        if "```python" in content:
            code = content.split("```python")[1].split("```")[0].strip()
        elif "```" in content:
            code = content.split("```")[1].split("```")[0].strip()
        else:
            code = content.strip()
            
        logger.info(f"Script generated ({len(code)} chars).")
        return {"bpy_code": code}
