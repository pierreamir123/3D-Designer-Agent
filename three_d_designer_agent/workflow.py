from typing import Dict, Any
from langgraph.graph import StateGraph
from .state import GraphState
from .analyst_agent import analyst_node
from .architect_agent import architect_node
from .validator_agent import validator_node
from .supervisor_agent import route_next


def create_3d_design_workflow():
    """
    Creates the LangGraph workflow for the 3D Designer Agent.
    """
    workflow = StateGraph(GraphState)
    
    # Add nodes to the graph
    workflow.add_node("analyst", analyst_node)
    workflow.add_node("architect", architect_node)
    workflow.add_node("validator", validator_node)
    
    # Add the supervisor node (for routing decisions)
    workflow.add_conditional_edges(
        "analyst",
        route_next,  # This will route to human_feedback after analysis
        {
            "architect": "architect",
            "human_feedback": "human_feedback",  # Placeholder for human intervention
            "complete": "complete",
            "analyst": "analyst"  # In case of errors
        }
    )
    
    # Add conditional edges for architect and validator
    workflow.add_conditional_edges(
        "architect",
        route_next,
        {
            "validator": "validator",
            "analyst": "analyst",  # If architect fails, return to analyst
            "complete": "complete"
        }
    )
    
    workflow.add_conditional_edges(
        "validator",
        route_next,
        {
            "complete": "complete",
            "analyst": "analyst",  # If validation fails, return to analyst to fix
            "architect": "architect"  # Or maybe to architect to adjust code
        }
    )
    
    # Set entry point
    workflow.set_entry_point("analyst")
    
    # Compile the graph
    return workflow.compile()


def approve_blueprint(state_data: Dict[str, Any]) -> GraphState:
    """
    Function to approve the blueprint after human review.
    This simulates the human-in-the-loop approval process.
    """
    updated_state = state_data.copy()
    updated_state["current_step"] = "approved"
    return GraphState(**updated_state)


def submit_feedback(user_input: str, current_state: GraphState) -> GraphState:
    """
    Submit user feedback to modify the design.
    """
    # Update the state with the new user input
    current_state.user_input = user_input
    
    # Reset the workflow to go back to the appropriate step based on feedback
    # For simplicity, we'll reset to initial to restart the process
    current_state.current_step = "initial"
    
    return current_state