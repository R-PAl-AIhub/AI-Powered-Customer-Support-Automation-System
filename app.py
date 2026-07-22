from langgraph.checkpoint.sqlite import SqliteSaver
from graph.workflow import build_graph
from langgraph.types import Command
from langchain_core.messages import HumanMessage

def run():
    with SqliteSaver.from_conn_string("chatbot.db") as memory:
        graph = build_graph(memory)
        config = {"configurable": {"thread_id": "customer_session_1"}}
        while True:
            print("\n=== AI-Powered Customer Support Automation System ===")
            user_message = input("Customer: ")
            if user_message.lower() == "exit":
                break
            
            initial_state = {
                "messages": [HumanMessage(content=user_message)],
                "needs_review": False,
            }

            result = graph.invoke(initial_state, config)

            
            while result.get("__interrupt__"):
                payload = result["__interrupt__"][0].value
                print("\n" + "="*40)
                print("⚠️  SUPERVISOR REVIEW REQUIRED")
                print("="*40)
                print(f"Customer : {user_message}")
                print(f"Draft    : {payload}")
                print("="*40)
                feedback = input("\nSupervisor — 'approve' or instructions: ")
                result = graph.invoke(Command(resume=feedback), config)

            # Graph finished — show the final answer.
            print(f"🧠 Memory: {len(result['messages'])} messages stored in this conversation")
            final = result.get("final_response") or result["messages"][-1].content
            print(f"\nAgent: {final}")


if __name__ == "__main__":
    run()