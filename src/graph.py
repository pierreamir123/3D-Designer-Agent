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

from src.agents.tester import TesterAgent
tester = TesterAgent()

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

def tester_node(state: GraphState):
    logger.info("\n" + "="*50)
    logger.info(">>> NODE: TESTER (QA)")
    logger.info("="*50)
    return tester.run(state)

def supervisor_node(state: GraphState):
    logger.info("\n" + "="*50)
    logger.info(">>> NODE: SUPERVISOR")
    logger.info("="*50)
    return {}

def route_supervisor(state: GraphState):
    logger.info(">>> SUPERVISOR (Routing)")
    decision = supervisor.run(state)
    return decision["next_agent"]

def route_validator(state: GraphState):
    errors = state.get("errors", [])
    retry_count = state.get("retry_count", 0)
    
    if errors:
        if retry_count < 3:
            logger.info(f"Validator found code errors (Attempt {retry_count + 1}/3). Retrying...")
            return "supervisor"
        else:
            logger.warning("Max retries reached in Validator.")
            return "end"
    return "tester"

def route_tester(state: GraphState):
    errors = state.get("errors", [])
    retry_count = state.get("retry_count", 0)
    
    if errors:
        if retry_count < 3:
            logger.info(f"Tester found quality issues (Attempt {retry_count + 1}/3). Routing back for enhancement...")
            return "supervisor"
        else:
            logger.warning("Max retries reached in Tester. Completing with best effort.")
            return "end"
    return "end"

# --- Graph Construction ---
workflow = StateGraph(GraphState)

# Add Nodes
workflow.add_node("analyst", analyst_node)
workflow.add_node("architect", architect_node)
workflow.add_node("coder", coder_node)
workflow.add_node("validator", validator_node)
workflow.add_node("tester", tester_node)
workflow.add_node("supervisor", supervisor_node)

# Set Entry Point
workflow.set_entry_point("supervisor")

# Conditional Routing from Supervisor
workflow.add_conditional_edges(
    "supervisor",
    route_supervisor,
    {
        "analyst": "analyst",
        "architect": "architect",
        "coder": "coder",
        "finish": END
    }
)

# Standard Flows
workflow.add_edge("analyst", "supervisor") 
workflow.add_edge("architect", "validator")
workflow.add_edge("coder", "validator")

# Validator Routing
workflow.add_conditional_edges(
    "validator",
    route_validator,
    {
        "supervisor": "supervisor", 
        "tester": "tester"
    }
)

# Tester Routing
workflow.add_conditional_edges(
    "tester",
    route_tester,
    {
        "supervisor": "supervisor",
        "end": END
    }
)

# Compile
# We interrupt after analyst (to review plan) and tester (to review final mesh)
app = workflow.compile(checkpointer=memory, interrupt_after=["analyst", "tester"]) 

