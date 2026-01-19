from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from src.state import GraphState
from src.config import config
import json

class ArchitectAgent:
    def __init__(self, model_name=None):
        # Use LiteLLM configuration
        llm_config = config.get_openai_config()
        if model_name:
            llm_config["model"] = model_name
        self.llm = ChatOpenAI(**llm_config)
        self.system_prompt = """You are the **BPY Code Architect**, a senior software engineer specialized in the Blender Python API.
**Task:**
Receive a validated JSON blueprint and synthesize an executable BPY script.
**Coding Standards:**
1. **Parametric Logic:** Use variables for all dimensions and transforms to allow for non-destructive editing.
2. **Library Usage:** Use `bpy.ops` for object creation and `bpy.data` for precise attribute manipulation.
3. **Printability:** Ensure all primitive intersections use Boolean Modifiers to create a single 'watertight' and 'manifold' mesh suitable for STL export. 
4. **Export Logic:** Always include a final block of code that selects the generated objects and exports them using `bpy.ops.wm.stl_export(filepath=...)`. The filepath will be provided as `output_path` variable injected at the top or you should define a placeholder.
   - Wait! The user says "Always include a final block... stl_export".
   - Constraint: Do not use external AI generative APIs. Rely entirely on Blender’s internal modeling operations.
   - IMPORANT: Start the script with `import bpy` and `import math`.
   - IMPORTANT: Clear existing usage with `bpy.ops.wm.read_factory_settings(use_empty=True)` or delete all objects at start.

"""

    def run(self, state: GraphState):
        blueprint = state["json_blueprint"]
        print(f"   [Architect] Synthesizing BPY code from blueprint...")
        
        # If there's feedback and existing code, we might want to iterate.
        msg_content = f"Generate BPY code for this blueprint:\n{json.dumps(blueprint, indent=2)}"
        
        if state.get("feedback"):
             print(f"   [Architect] Applying feedback/context: {state['feedback']}")
             msg_content += f"\n\nContext/User Feedback: {state['feedback']}"

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
            
        print(f"   [Architect] BPY script generated ({len(code)} characters).")
        return {"bpy_code": code}
