from typing import TypedDict,Optional,Annotated
from langgraph.graph.message import add_messages

class CustomerSupportState(TypedDict):
    messages: Annotated[list,add_messages] #Stores the previous messages
    customer_queries:Optional[str] #stores the customer queries
    classify_customer_issue: Optional[str] # classify the customer queries
    support_department: Optional[str] # Store which concerned department needs to take action
    ai_draft: Optional[str] #The response made by ai
    human_feedback: Optional[str]  #the response by by human in case of human in loop
    kb_context:Optional[str] #contains relevant compan's documentation
    needs_review: Optional[bool] #Checks if human review is needed
    final_response:Optional[str] # Stores the final response after a human review

