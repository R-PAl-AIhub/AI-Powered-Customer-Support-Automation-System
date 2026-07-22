from langchain_core.messages import AIMessage
from utils.llm import llm
from knowldgeBase.database_retriver import retriver
from graph.CustomerSupportState import CustomerSupportState
from utils.escalation import needs_human
from utils.history import format_history

def Account_Agent(state:CustomerSupportState)->CustomerSupportState:
    user_query = state["messages"][-1].content
    history = format_history(state["messages"])
    docs = retriver.invoke(user_query)
    context = "\n".join(
        doc.page_content for doc in docs
    )
    print(f"🤖 Agent: Account_Agent")
    print(f"📚 Retrieved {len(docs)} KB chunks:\n{context[:300]}...\n")
    prompt = f"""
You are the Account Support Agent for ABC Technologies.

You help customers with account-related questions: password resets, profile
updates, account activation/deactivation, email/username changes, and account
access. Never claim an account has actually been modified — only give guidance
based on the context.

Use the conversation history to understand follow-up questions, and ONLY the
context below for facts. Return ONLY the final customer-facing reply: friendly,
clear, and step-by-step when helpful. Do not include the context, your
reasoning, or any internal notes.

Conversation history:
{history}

Context:
{context}

Current query:
{user_query}
"""
    result = llm.invoke(prompt)

    review = needs_human(user_query)

    return {"messages":[AIMessage(content=result.content)],
            "needs_review":review,
            "kb_context":context,
            "ai_draft":result.content
            }
