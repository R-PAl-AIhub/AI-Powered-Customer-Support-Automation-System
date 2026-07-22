"""Format prior conversation turns so agents can answer follow-up questions."""


def format_history(messages, limit: int = 8) -> str:
    """Return the recent conversation (excluding the current query) as plain text.

    `messages` is the state's message list; the last item is the current query,
    so it is left out here and passed to the prompt separately.
    """
    prior = messages[:-1][-limit:]
    if not prior:
        return "(no previous conversation)"

    lines = []
    for m in prior:
        role = "Customer" if m.type == "human" else "Agent"
        lines.append(f"{role}: {m.content}")
    return "\n".join(lines)
