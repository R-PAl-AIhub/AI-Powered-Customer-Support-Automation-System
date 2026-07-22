from graph.CustomerSupportState import CustomerSupportState
from utils.llm import llm

def revise_response(state: CustomerSupportState) -> CustomerSupportState:
    user_query = state["messages"][0].content
    prompt = f"""You are a customer support agent. Rewrite the draft reply below
using the supervisor's feedback.

Return ONLY the final customer-facing message. Do NOT include the context,
policies, your reasoning, or any internal notes.

Customer question: {user_query}
Current draft: {state['ai_draft']}
Supervisor feedback: {state['human_feedback']}

Final reply:"""

    response = llm.invoke(prompt)
    print(f"\n🤖 Response revised.")
    return {"ai_draft": response.content}
