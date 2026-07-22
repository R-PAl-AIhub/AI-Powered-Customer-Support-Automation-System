from graph.CustomerSupportState import CustomerSupportState
from langgraph.types import interrupt

def human_review_node(state: CustomerSupportState) -> CustomerSupportState:
    feedback = interrupt(state["ai_draft"])
    return {"human_feedback": feedback}



