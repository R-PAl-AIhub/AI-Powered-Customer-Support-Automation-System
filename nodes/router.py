from graph.CustomerSupportState import CustomerSupportState

def router(state: CustomerSupportState):
    label = state["classify_customer_issue"]
    print(f"\n🧭 Classified as: {label}")

    if label == "Sales":
        return "Sales_Agent"

    elif label == "Technical Support":
        return "Technical_Agent"

    elif label == "Billing":
        return "Billing_Agent"

    elif label == "Account":
        return "Account_Agent"

    else:
        # General / anything unrecognised → handled by the Account agent,
        # which can also answer follow-up and memory-recall questions.
        return "Account_Agent"
