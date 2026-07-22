from langgraph.graph import StateGraph
from graph.CustomerSupportState import CustomerSupportState
from nodes.classifyQuery import classifyQuery
from nodes.finalize import finalize
from nodes.human_review_node import human_review_node 
from nodes.revise_response import revise_response
from nodes.route_after_draft import route_after_draft
from nodes.route_after_review import route_after_review
from nodes.router import router
from agents.account_agent import Account_Agent
from agents.billing_agent import Billing_Agent
from agents.sales_agent import Sales_Agent
from agents.technical_support import Technical_Agent


def build_graph(checkpointer):

    builder = StateGraph(CustomerSupportState)
    builder.add_node("classifyQuery",classifyQuery)
    builder.add_node("finalize",finalize)
    builder.add_node("human_review",human_review_node)
    builder.add_node("Account_Agent",Account_Agent)
    builder.add_node("Billing_Agent",Billing_Agent)
    builder.add_node("Sales_Agent",Sales_Agent)
    builder.add_node("Technical_Agent",Technical_Agent)
    builder.add_node("revise_response",revise_response)

    builder.set_entry_point("classifyQuery")
    builder.add_conditional_edges("classifyQuery",router)
    builder.add_conditional_edges("Sales_Agent",route_after_draft)
    builder.add_conditional_edges("Account_Agent",route_after_draft)
    builder.add_conditional_edges("Billing_Agent",route_after_draft)
    builder.add_conditional_edges("Technical_Agent",route_after_draft)

    builder.add_conditional_edges("human_review",route_after_review)
    builder.add_edge("revise_response","human_review")
    builder.set_finish_point("finalize")
    return builder.compile(
        checkpointer=checkpointer
    )







