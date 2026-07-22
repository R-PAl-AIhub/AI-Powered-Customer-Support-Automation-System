from graph.CustomerSupportState import CustomerSupportState
from typing import Literal

def route_after_review(state: CustomerSupportState) -> Literal["revise_response", "finalize"]:
    feedback = (state["human_feedback"] or "").lower()
    approved = any(word in feedback for word in ["approve", "approved", "yes", "ok", "looks good"])
    return "finalize" if approved else "revise_response"
