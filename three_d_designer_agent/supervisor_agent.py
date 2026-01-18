from typing import Dict, Any, Literal
from langgraph.graph import END
from .state import GraphState
from .analyst_agent import analyst_node
from .architect_agent import architect_node
from .validator_agent import validator_node


def supervisor_node(state: GraphState) -> Dict[str, Any]:
    """
    Supervisor Agent: Orchestration & UI Handler
    Manages the LangGraph state and routes Gradio text modifications.
    """
    print(f"Supervisor checking current step: {state.current_step}")
    
    # Determine next action based on current state
    if state.current_step == "initial":
        return {"next": "analyst"}
    elif state.current_step == "analysis_complete":
        return {"next": "architect"}
    elif state.current_step == "architect_complete":
        return {"next": "validator"}
    elif state.current_step == "validation_complete":
        return {"next": "complete"}
    elif state.current_step in ["analysis_failed", "architect_failed", "validation_failed", "validation_error"]:
        # In a real implementation, we might have error recovery logic here
        return {"next": END}
    else:
        return {"next": END}


def route_based_on_feedback(state: GraphState) -> Literal["analyst", "architect", "validator", "complete"]:
    """
    Route the workflow based on user feedback.
    Determines if feedback requires structural change (analyst) or property change (architect).
    """
    user_input_lower = state.user_input.lower()
    
    # Keywords that suggest structural changes (require analyst)
    structural_keywords = [
        "shape", "geometry", "structure", "form", "layout", "design", 
        "add", "remove", "change shape", "modify structure"
    ]
    
    # Keywords that suggest property changes (can go straight to architect)
    property_keywords = [
        "size", "dimension", "scale", "color", "material", "position", 
        "rotate", "move", "resize", "thickness", "width", "height", "depth"
    ]
    
    # Check if the feedback involves structural changes
    for keyword in structural_keywords:
        if keyword in user_input_lower:
            return "analyst"
    
    # Check if the feedback involves property changes
    for keyword in property_keywords:
        if keyword in user_input_lower:
            return "architect"
    
    # Default to analyst for any significant change
    return "analyst"


# Define the conditional edges for the graph
def route_next(state: GraphState) -> Literal["analyst", "architect", "validator", "human_feedback", "complete"]:
    """
    Conditional edge routing based on current state.
    """
    if state.current_step == "initial":
        return "analyst"
    elif state.current_step == "analysis_complete":
        # After analysis, we need human approval/intervention before proceeding
        return "human_feedback"  # This represents the interrupt point
    elif state.current_step == "approved":  # After human approval
        return "architect"
    elif state.current_step == "architect_complete":
        return "validator"
    elif state.current_step == "validation_complete":
        return "complete"
    elif state.current_step in ["analysis_failed", "architect_failed", "validation_failed"]:
        return "analyst"  # Return to analyst for correction
    else:
        return END