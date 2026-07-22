"""Deterministic check for whether a customer query needs human approval.

Small models are unreliable at following a 'return the word human' instruction,
so escalation is decided in code from the customer's query instead.
"""

ESCALATION_TRIGGERS = [
    "refund",
    "money back",
    "cancel",
    "cancellation",
    "close my account",
    "close account",
    "account closure",
    "delete my account",
    "compensation",
    "escalate",
    "speak to a manager",
    "speak to manager",
]


def needs_human(text: str) -> bool:
    """Return True if the query mentions an action that requires supervisor approval."""
    t = text.lower()
    return any(trigger in t for trigger in ESCALATION_TRIGGERS)
