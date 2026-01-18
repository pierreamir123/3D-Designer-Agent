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
        input_data = state["input_data"]
        messages = [SystemMessage(content=self.system_prompt)]
        
        # Check if input is likely an image path or text
        # For simplicity in this demo, if it looks like a path, we treat it as image, else text
        # (In a real app, we'd check extensions)
        if hasattr(input_data, "lower") and (input_data.lower().endswith(('.png', '.jpg', '.jpeg'))):
             # Assuming we have a way to Load image content, or pass URL. 
             # OpenAI accepts base64 or urls. 
             # For this scaffold, we will assume input is text description for now 
             # UNLESS the user explicitly handles image loading. 
             # Let's assume text for the MVP unless updated.
             content = [{"type": "text", "text": "Analyze this 3D object:"}, 
                        {"type": "image_url", "image_url": {"url": f"file://{input_data}"}}] # Local file URI scheme might fail depending on LangChain version, usually needs base64
             # For safety/speed, let's just stick to text processing for the scaffold 
             # or user description if provided.
             pass 

        # Simple text handling
        messages.append(HumanMessage(content=f"Decompose this object: {input_data}"))
        
        if state.get("feedback"):
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
        except json.JSONDecodeError:
            blueprint = {"error": "Failed to parse JSON", "raw": content}

        return {"json_blueprint": blueprint}
