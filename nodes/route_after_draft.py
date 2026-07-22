from graph.CustomerSupportState import CustomerSupportState
from typing import Literal

def route_after_draft(state: CustomerSupportState) -> Literal["human_review", "finalize"]:
    return "human_review" if state["needs_review"] else "finalize"