from langchain_core.messages import AIMessage
from utils.llm import llm
from knowldgeBase.database_retriver import retriver
from graph.CustomerSupportState import CustomerSupportState
from utils.escalation import needs_human
from utils.history import format_history

def Sales_Agent(state:CustomerSupportState)->CustomerSupportState:
    user_query = state["messages"][-1].content
    history = format_history(state["messages"])
    docs = retriver.invoke(user_query)
    context = "\n".join(
        doc.page_content for doc in docs
    )
    print(f"🤖 Agent: Sales_Agent")
    print(f"📚 Retrieved {len(docs)} KB chunks:\n{context[:300]}...\n")
    prompt = f"""
You are the Sales Agent for ABC Technologies.

Use the conversation history to understand follow-up questions, and ONLY the
context below for facts. Return ONLY the final customer-facing reply: friendly,
concise, and accurate. Do not include the context, your reasoning, or any
internal notes.

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
