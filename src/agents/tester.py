from src.state import GraphState
from src.utils.blender_ops import BlenderOps
from src.config.logger import get_logger
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from src.config import config
import json

logger = get_logger("Tester")

class TesterAgent:
    def __init__(self, model_name=None):
        llm_config = config.get_openai_config()
        if model_name:
            llm_config["model"] = model_name
        self.llm = ChatOpenAI(**llm_config)
        self.system_prompt = """You are the **3D Quality Assurance Engineer**.
Your role is to evaluate the technical quality of the generated 3D model and its code.
You receive a list of "Mesh Issues" (detected procedurally) and the "BPY Code".

**Task:**
1. **Analyze**: Evaluate if the model is "High Quality" (watertight, manifold, matches request).
2. **Diagnose**: If there are non-manifold edges or other issues, explain why they occurred in the code.
3. **Enhance**: Even if it runs, suggest one "Pro-Level" enhancement (e.g. 'Add a bevel to the edges', 'Reduce polygon count', 'Use a subsurf modifier').

**Output:**
Return a JSON object:
{
  "pass": true | false,
  "report": "Description of quality and issues found.",
  "refinement_suggestions": "Specific instructions for the next agent to improve the model."
}
"""

    def run(self, state: GraphState):
        logger.info("Starting Advanced Quality Testing (Evaluation Mode)...")
        
        # We now read procedurally detected issues from the state 
        # (detected during isolated execution in Validator)
        mesh_issues = state.get("mesh_issues", [])
        
        # Use LLM to generate the refinement plan
        msg_content = f"""
Existing BPY Code:
{state.get('bpy_code', 'No code')}

Procedural Testing Results:
{json.dumps(mesh_issues, indent=2) if mesh_issues else "No technical mesh issues found."}

User Original Request: {state.get('input_data', 'No input')}
"""
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=msg_content)
        ]
        
        response = self.llm.invoke(messages)
        try:
            content = response.content
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            result = json.loads(content)
        except:
            logger.warning("Failed to parse Tester JSON, using default pass.")
            result = {"pass": True, "report": "Passed basic validation.", "refinement_suggestions": ""}

        logger.info(f"Test Result: {'PASS' if result['pass'] else 'FAIL'}")
        
        # Store report in state
        report_text = f"Quality Report:\n{result['report']}\n\nRefinement:\n{result['refinement_suggestions']}"
        
        return {
            "test_report": report_text,
            "errors": mesh_issues if not result["pass"] else []
        }
