from langgraph.graph import StateGraph, END
from src.state import GraphState
from src.agents.analyst import AnalystAgent
from src.agents.architect import ArchitectAgent
from src.agents.validator import ValidatorAgent
from src.agents.supervisor import SupervisorAgent
from src.agents.coder import CoderAgent
from langgraph.checkpoint.memory import MemorySaver
from src.config.logger import get_logger

logger = get_logger("Graph")

# Initialize Agents
analyst = AnalystAgent()
architect = ArchitectAgent()
validator = ValidatorAgent()
supervisor = SupervisorAgent()
coder = CoderAgent()

memory = MemorySaver()

# --- Node Functions ---

def analyst_node(state: GraphState):
    logger.info("\n" + "="*50)
    logger.info(">>> NODE: ANALYST")
    logger.info("="*50)
    return analyst.run(state)

def architect_node(state: GraphState):
    logger.info("\n" + "="*50)
    logger.info(">>> NODE: ARCHITECT")
    logger.info("="*50)
    return architect.run(state)

def coder_node(state: GraphState):
    logger.info("\n" + "="*50)
    logger.info(">>> NODE: CODER")
    logger.info("="*50)
    return coder.run(state)

def validator_node(state: GraphState):
    logger.info("\n" + "="*50)
    logger.info(">>> NODE: VALIDATOR")
    logger.info("="*50)
    return validator.run(state)

def route_supervisor(state: GraphState):
    logger.info(">>> NODE: SUPERVISOR (Routing)")
    decision = supervisor.run(state)
    return decision["next_agent"]

def route_validator(state: GraphState):
    errors = state.get("errors", [])
    retry_count = state.get("retry_count", 0)
    
    if errors:
        if retry_count < 3:
            logger.info(f"Validation failed (Attempt {retry_count + 1}/3). Retrying...")
            # Route back to Supervisor to decide who fixes it (Architect or Coder)
            return "supervisor"
        else:
            logger.warning("Max retries reached. Stopping execution.")
            return "end"
    return "end"

# --- Graph Construction ---
workflow = StateGraph(GraphState)

# Add Nodes
workflow.add_node("analyst", analyst_node)
workflow.add_node("architect", architect_node)
workflow.add_node("coder", coder_node)
workflow.add_node("validator", validator_node)
workflow.add_node("supervisor", route_supervisor)

# Set Entry Point
# We start at Supervisor to allow routing to Coder vs Analyst based on prompt
workflow.set_entry_point("supervisor")

# Conditional Routing from Supervisor
workflow.add_conditional_edges(
    "supervisor",
    route_supervisor,
    {
        "analyst": "analyst",
        "architect": "architect",
        "coder": "coder"
    }
)

# Standard Flows
workflow.add_edge("analyst", "supervisor") # After analysis, re-route (often stops at interrupt if configured)
workflow.add_edge("architect", "validator")
workflow.add_edge("coder", "validator")

# Validator Routing (Success -> End, Fail -> Repair)
workflow.add_conditional_edges(
    "validator",
    route_validator,
    {
        "supervisor": "supervisor", # Go back to supervisor to dispatch repair
        "end": END
    }
)

# Compile
# interrupt_after=["analyst"] allows user to review the blueprint if Analyst was called.
app = workflow.compile(checkpointer=memory, interrupt_after=["analyst"])
