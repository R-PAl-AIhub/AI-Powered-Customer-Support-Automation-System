from graph.CustomerSupportState import CustomerSupportState
from utils.llm import llm
from langchain_core.messages import HumanMessage,AIMessage

def classifyQuery(state: CustomerSupportState)->CustomerSupportState:
   user_query = state["messages"][-1].content 
   prompt = f"""
            You are an intent classification model.
            Your task is to classify the user's query into exactly ONE of the following categories:\n\n

               1. Sales
                  - Product information
                  - Subscription plans
                  - Pricing details
                  - Purchase-related questions
                  - Feature comparisons
               \n\n
               2. Technical Support
                  - Application errors
                  - Installation issues
                  - Login problems
                  - Configuration issues
                  - Bugs
                  - Performance issues
                  - Troubleshooting
               \n\n
               3. Billing
                  - Invoice requests
                  - Payment issues
                  - Refund requests
                  - Charges
                  - Billing history
                  - Payment failures
               \n\n
               4. Account
                  - Password reset
                  - Profile updates
                  - Account activation
                  - Account deactivation
                  - Account settings
                  - Username/email changes
               \n\n
               Rules:
               - Return ONLY one category.
               - Do NOT explain your reasoning.
               - Do NOT output any additional text.
               - Do NOT use punctuation.
               - If multiple topics are mentioned, choose the category that best represents the user's primary intent.
               
               \n\n
               Valid outputs are exactly one of:
               Sales
               Technical Support
               Billing
               Account
              

               User Query:
               {user_query}
            """
   response = llm.invoke(prompt)

   category = response.content.strip()
   state["classify_customer_issue"] = category
   return {"classify_customer_issue":category,
           "customer_queries":user_query}

if __name__ =="__main__":
   state: CustomerSupportState = {
        "messages": [HumanMessage(content="I forgot my account password.")]
    }

   state = classifyQuery(state)
   print(state["classify_customer_issue"])

	


