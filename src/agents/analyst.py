import json
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from src.state import GraphState
from src.config import config

class AnalystAgent:
    def __init__(self, model_name=None):
        # Use LiteLLM configuration
        llm_config = config.get_openai_config()
        if model_name:
            llm_config["model"] = model_name
        self.llm = ChatOpenAI(**llm_config)
        self.system_prompt = """You are the **Visual Decomposition Specialist**. Your role is to perform 3D reverse engineering on 2D inputs.
**Task:**
Decompose the object in the provided image or description into its fundamental geometric primitives (Cubes, Cylinders, UV Spheres, Tori, Cones).
**Output Requirements:**
You must output a valid JSON schema representing the 'Reverse Engineering Blueprint'.
* **primitive_type**: Must be a standard Blender primitive (Cube, Cylinder, UV Sphere, Torus, Cone).
* **dimensions**: Precise scale factors or radius/depth.
* **transform**: Location and Rotation in radians.
* **boolean_op**: Specify if the part should be joined (UNION) or used as a cutter (DIFFERENCE).

**Operational Constraint:**
Do not write Python code. Provide only the JSON structure. Your output will be used for human review before any code generation occurs.
Wrap your JSON output in ```json ... ``` blocks so it can be parsed easily.
"""

    def run(self, state: GraphState):
        print(f"   [Analyst] Analyzing input: {state.get('input_data', 'No input')[:50]}...")
        input_data = state["input_data"]
        messages = [SystemMessage(content=self.system_prompt)]
        
        # ... logic ...
        
        # Simple text handling
        messages.append(HumanMessage(content=f"Decompose this object: {input_data}"))
        
        if state.get("feedback"):
             print(f"   [Analyst] incorporating user feedback: {state['feedback']}")
             messages.append(HumanMessage(content=f"User Feedback on previous iteration: {state['feedback']}"))

        response = self.llm.invoke(messages)
        
        # Parse JSON from markdown
        content = response.content
        if "```json" in content:
            json_str = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            json_str = content.split("```")[1].split("```")[0].strip()
        else:
            json_str = content
            
        try:
            blueprint = json.loads(json_str)
            print(f"   [Analyst] Successfully generated blueprint with {len(blueprint.get('primitives', []))} primitives.")
        except json.JSONDecodeError:
            print("   [Analyst] Error: Failed to parse JSON response from LLM.")
            blueprint = {"error": "Failed to parse JSON", "raw": content}

        return {"json_blueprint": blueprint}
