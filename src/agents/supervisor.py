from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from src.state import GraphState
from src.config import config
from src.config.logger import get_logger
import json

logger = get_logger("Supervisor")

class SupervisorAgent:
    def __init__(self, model_name=None):
        # Use LiteLLM configuration
        llm_config = config.get_openai_config()
        if model_name:
            llm_config["model"] = model_name
        self.llm = ChatOpenAI(**llm_config)
        self.system_prompt = """You are the **Workflow Supervisor**.
Your goal is to route the user's request to the appropriate worker agent.
**Workers:**
1.  **analyst**: visual decomposition (default for "design", "make", "create" object requests).
2.  **architect**: generates BPY code from a JSON blueprint (from analyst).
3.  **coder**: generates BPY code DIRECTLY (use for "script", "code", "python", "procedural" requests).

**Routing Logic:**
*   If the user asks to "make a [shape]", "design a [object]" -> **analyst**.
*   If the user asks to "write a script", "generate code", "python" -> **coder**.
*   If there is feedback on a BLUEPRINT -> **analyst**.
*   If there is feedback on a 3D MODEL/CODE -> **architect** (or **coder** if code-based).
*   If `errors` exist -> **architect** (or **coder**).

**Output:**
Return a JSON object: `{"next_agent": "analyst" | "architect" | "coder"}`.
"""

    def run(self, state: GraphState):
        feedback = state.get("feedback")
        errors = state.get("errors")
        
        logger.info(f"Evaluating next step. Feedback provided: {bool(feedback)}, Errors present: {bool(errors)}")

        # If there are errors from validator, we force back to architect
        if errors:
            logger.info(f"Routing back to ARCHITECT to fix {len(errors)} error(s).")
            return {"next_agent": "architect"}
            
        if not feedback:
            logger.info("No feedback provided, proceeding to ARCHITECT.")
            return {"next_agent": "architect"}

        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=f"User Feedback: {feedback}")
        ]
        
        response = self.llm.invoke(messages)
        content = response.content
        
        try:
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            result = json.loads(content)
            
            # Safety check: if result is a list, extract the first dict if possible or default
            if isinstance(result, list) and len(result) > 0 and isinstance(result[0], dict):
                result = result[0]
            elif not isinstance(result, dict):
                result = {"next_agent": "architect"}

            logger.info(f"Decision: Route to {result.get('next_agent', 'architect').upper()}.")
            return result
        except Exception as e:
            logger.error(f"Error parsing decision: {str(e)}. Raw content: {content[:200]}...")
            return {"next_agent": "architect"}
