from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from src.state import GraphState
import json

class SupervisorAgent:
    def __init__(self, model_name="gpt-4o"):
        self.llm = ChatOpenAI(model=model_name, temperature=0)
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
        
        # If there are errors from validator, we force back to architect (or we could let specific logic handle it, but supervisor can do it)
        if errors:
            return {"next_agent": "architect"}
            
        if not feedback:
            # If no feedback and no errors, and we just came from Analyst (implied by flow), 
            # we assume approval? Or maybe we wait.
            # But usually this node is called AFTER human input.
            # If empty feedback, assume proceed to architect.
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
            return result
        except:
            # Fallback
            return {"next_agent": "architect"}
