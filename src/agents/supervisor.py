from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from src.state import GraphState
from src.config import config
import json

class SupervisorAgent:
    def __init__(self, model_name=None):
        # Use LiteLLM configuration
        llm_config = config.get_openai_config()
        if model_name:
            llm_config["model"] = model_name
        self.llm = ChatOpenAI(**llm_config)
        self.system_prompt = """You are the **3D Agent Supervisor**. 
You orchestrate the flow between the Analyst, the Architect, and the Human-in-the-loop.

**Task:**
Analyze the user's text feedback and the current state to decide the next step.

**Routing Rules:**
1. If the user feedback implies a **structural change** (e.g., "add a leg", "change shape to sphere", "remove the top"), route to **Analyst**.
2. If the user feedback implies a **property change** (e.g., "make it thicker", "rotate it", "move it up", "red"), route to **Architect**.
3. If the user just approved or said "looks good" or "build it", and we haven't built it yet, route to **Architect**.
4. If we just finished validation and there are errors, route to **Architect** to fix them. (This might be handled by Validator edges, but good to know).

**Output:**
Return a JSON with a single key "next_agent" which can be "analyst" or "architect".
"""

    def run(self, state: GraphState):
        feedback = state.get("feedback")
        errors = state.get("errors")
        
        print(f"   [Supervisor] Evaluating next step. Feedback: {feedback[:30] if feedback else 'None'}, Errors: {bool(errors)}")

        # If there are errors from validator, we force back to architect
        if errors:
            print(f"   [Supervisor] Routing back to ARCHITECT to fix {len(errors)} error(s).")
            return {"next_agent": "architect"}
            
        if not feedback:
            print("   [Supervisor] No feedback provided, proceeding to ARCHITECT.")
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
            print(f"   [Supervisor] Decision: Route to {result.get('next_agent', 'architect').upper()}.")
            return result
        except:
            print("   [Supervisor] Error parsing decision, defaulting to ARCHITECT.")
            return {"next_agent": "architect"}
