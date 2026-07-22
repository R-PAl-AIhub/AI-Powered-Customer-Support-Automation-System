from graph.CustomerSupportState import CustomerSupportState

def finalize(state: CustomerSupportState) -> CustomerSupportState:
    return {"final_response": state["ai_draft"]}