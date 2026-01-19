import json
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from src.state import GraphState
from src.config import config
from src.config.logger import get_logger

logger = get_logger("Analyst")

class AnalystAgent:
    def __init__(self, model_name=None):
        # Use LiteLLM configuration
        llm_config = config.get_openai_config()
        if model_name:
            llm_config["model"] = model_name
        self.llm = ChatOpenAI(**llm_config)
        self.system_prompt = """You are the **Visual Decomposition Specialist**. Your role is to perform 3D reverse engineering on 2D inputs.
**Task:**
1. **Analyze**: First, describe the object's structure in natural language. Think about how to break it down into simple shapes.
2. **Decompose**: Then, create a JSON blueprint of the fundamental geometric primitives (Cubes, Cylinders, UV Spheres, Tori, Cones).

**Output Requirements:**
You must output a JSON object with two keys:
*   "reasoning": A string containing your step-by-step structural analysis.
*   "blueprint": A valid JSON schema representing the 3D plan.

**Blueprint Schema:**
*   **primitive_type**: Must be a standard Blender primitive.
*   **dimensions**: Precise scale factors.
*   **transform**: Location and Rotation.
*   **boolean_op**: UNION or DIFFERENCE.

**Operational Constraint:**
Wrap your JSON output in ```json ... ``` blocks.
"""

    def run(self, state: GraphState):
        logger.info(f"Analyzing input: {state.get('input_data', 'No input')[:50]}...")
        input_data = state["input_data"]
        messages = [SystemMessage(content=self.system_prompt)]
        
        # Simple text handling
        messages.append(HumanMessage(content=f"Decompose this object: {input_data}"))
        
        if state.get("feedback"):
             logger.info(f"Incorporating user feedback: {state['feedback']}")
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
            parsed = json.loads(json_str)
            # Handle both new CoT format and potential legacy format
            if "reasoning" in parsed and "blueprint" in parsed:
                reasoning = parsed["reasoning"]
                blueprint = parsed["blueprint"]
            else:
                reasoning = "No explicit reasoning provided."
                blueprint = parsed

            # Safety check for list-based blueprints
            if isinstance(blueprint, list):
                blueprint = {"primitives": blueprint}
            
            num_primitives = len(blueprint.get('primitives', [])) if isinstance(blueprint, dict) else "unknown"
            logger.info(f"Analysis Complete. Reasoning: {reasoning[:100]}...")
            logger.info(f"Blueprint generated with {num_primitives} primitives.")
            
            return {"json_blueprint": blueprint, "reasoning": reasoning, "retry_count": 0}
        except json.JSONDecodeError:
            logger.error(f"Failed to parse JSON response from LLM. Raw content: {content[:200]}...")
            blueprint = {"error": "Failed to parse JSON", "raw": content}

        return {"json_blueprint": blueprint, "retry_count": 0}
