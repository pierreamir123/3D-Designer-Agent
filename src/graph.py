from langgraph.graph import StateGraph, END
from src.state import GraphState
from src.agents.analyst import AnalystAgent
from src.agents.architect import ArchitectAgent
from src.agents.validator import ValidatorAgent
from langgraph.checkpoint.memory import MemorySaver
from src.agents.supervisor import SupervisorAgent

# Initialize Agents
analyst = AnalystAgent()
architect = ArchitectAgent()
validator = ValidatorAgent()
supervisor = SupervisorAgent()

memory = MemorySaver()

def analyst_node(state: GraphState):
    print("---ANALYST---")
    return analyst.run(state)

def supervisor_node(state: GraphState):
    print("---SUPERVISOR---")
    # This node just determines routing, but in LangGraph we often return state updates.
    # Supervisor run returns {"next_agent": ...} which isn't part of GraphState directly unless we add it
    # or we use it in the conditional edge. 
    # Let's effectively just pass through here, or store 'next_agent' in state if needed.
    # Actually, we can make the supervisor logic PART of the conditional edge function.
    # But to keep it modular as an 'Agent', let's run it here and store decision in a temp key or use return.
    # For simplicity, let's strictly return the decision in a key 'next_step' in state? 
    # Or better: Use the agent instance inside the conditional edge function.
    # Let's do the latter for cleaner graph, OR have this node update 'feedback_classification'.
    return {} 

def architect_node(state: GraphState):
    print("---ARCHITECT---")
    return architect.run(state)

def validator_node(state: GraphState):
    print("---VALIDATOR---")
    return validator.run(state)

def route_supervisor(state: GraphState):
    # logic from supervisor agent
    decision = supervisor.run(state)
    return decision["next_agent"]

def route_validator(state: GraphState):
    if state.get("errors"):
        return "architect"
    return "end"

# Build Graph
workflow = StateGraph(GraphState)

workflow.add_node("analyst", analyst_node)
workflow.add_node("architect", architect_node)
workflow.add_node("validator", validator_node)

# We normally start at Analyst
workflow.set_entry_point("analyst")

# After Analyst, we "interrupt" for user. 
# LangGraph doesn't have an explicit "Interrupt Node" per se, it has 'interrupt_before' or 'interrupt_after' 
# when compiling the graph.
# So we just define the edge: Analyst -> Supervisor (where Supervisor logic runs)
# BUT we want the graph to STOP after Analyst so user can see JSON.
# So we will compile with `interrupt_after=["analyst"]`.

# From Analyst, we go to "supervisor_routing" logic.
# Since we need a node to resume INTO from interrupt (or we resume from the next node), 
# let's add a dummy node or just use the conditional edge from Analyst?
# If we interrupt AFTER Analyst, the next step hasn't run.
# When we resume, we usually update state (feedback) and then proceed.
# If we proceed 'from' Analyst, we need to know where to go.
# So let's insert a 'router' node that we resume into?
# Or simply: Analyst -> Router.
workflow.add_node("router", lambda x: {}) # Dummy node to act as decision point?
# Actually, the Supervisor Agent IS the router.

workflow.add_edge("analyst", "router")

workflow.add_conditional_edges(
    "router",
    route_supervisor,
    {
        "analyst": "analyst",
        "architect": "architect"
    }
)

workflow.add_edge("architect", "validator")

workflow.add_conditional_edges(
    "validator",
    route_validator,
    {
        "architect": "architect",
        "end": END
    }
)

# Compile
app = workflow.compile(checkpointer=memory, interrupt_after=["analyst"]) 
# Wait, if we interrupt after analyst, the user provides feedback.
# Then we resume. The next node is 'router'.
# Router calls Supervisor logic which checks feedback. 
# Perfect.

