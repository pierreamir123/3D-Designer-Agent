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
1.  **analyst**: visual decomposition. Use this for NEW design requests or structural changes to the plan.
2.  **architect**: generates BPY code from the existing blueprint. Use this when the user says "Proceed", "Build", "Go", or "Looks good". 
3.  **coder**: generates BPY code DIRECTLY. Use this for "write a script", "procedural code", etc.

**Routing Logic:**
*   **Approval**: Any variation of "Proceed", "Build", "Looks good", "Yes" -> **architect**.
*   **Completion**: If the user says "Thanks", "Perfect", "Done", or nothing new is requested -> **finish**.
*   **New Design**: "Make a...", "Create a..." -> **analyst**.
*   **Scripting**: "Write a python script...", "Generate code to..." -> **coder**.
*   **Re-Analysis**: If the user wants to ADD parts or change the structure of the blueprint -> **analyst**.
*   **Fixes**: If there are code errors -> **architect** (or **coder**).

**Output:**
Return a JSON object: `{"next_agent": "analyst" | "architect" | "coder" | "finish"}`.
"""

    def run(self, state: GraphState):
        feedback = (state.get("feedback") or "").lower().strip()
        errors = state.get("errors")
        input_data = state.get("input_data")
        blueprint = state.get("json_blueprint")
        test_report = state.get("test_report")
        
        logger.info(f"Evaluating next step. Feedback: '{feedback}', Errors: {bool(errors)}, Has Test Report: {bool(test_report)}")

        # 0. EXIT CONDITION: If no feedback and we already have a successful build
        if not feedback and blueprint and not errors and test_report:
            logger.info("No new feedback and build successful. Routing to FINISH.")
            return {"next_agent": "finish"}

        # 1. KEYWORD OVERRIDES
        approval_keywords = ["proceed", "build", "looks good", "go", "yes", "confirm", "generate"]
        if any(k in feedback for k in approval_keywords) and blueprint:
            logger.info("Universal Approval detected. Routing to ARCHITECT.")
            return {"next_agent": "architect"}

        # 1. Handle Errors/Quality Issues (Self-Correction)
        if errors or (test_report and "Fail" in test_report):
            next_agent = "coder" if not blueprint else "architect"
            logger.info(f"Routing back to {next_agent.upper()} to fix errors/quality issues.")
            return {"next_agent": next_agent}
            
        # 2. Handle Initial Request or Feedback
        prompt_input = feedback if feedback else input_data
        
        # Inject Test Report context if we are iterating
        if test_report:
            prompt_input += f"\n\nTECHNICAL TEST REPORT:\n{test_report}"
        
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=f"User Request/Feedback: {prompt_input}")
        ]
        
        response = self.llm.invoke(messages)
        content = response.content
        
        try:
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            result = json.loads(content)
            
            # Fallback based on state
            default_agent = "analyst" if not blueprint else "architect"

            # Safety check: if result is a list, extract the first dict if possible or default
            if isinstance(result, list) and len(result) > 0 and isinstance(result[0], dict):
                result = result[0]
            elif not isinstance(result, dict):
                result = {"next_agent": default_agent}

            decision = result.get('next_agent', default_agent)
            logger.info(f"Decision: Route to {decision.upper()}.")
            return {"next_agent": decision}
        except Exception as e:
            default_agent = "analyst" if not blueprint else "architect"
            logger.error(f"Error parsing decision: {str(e)}. Raw content: {content[:200]}...")
            return {"next_agent": default_agent}
