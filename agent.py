import os
from typing import Annotated, TypedDict
from langchain_openai import ChatOpenAI # Meta uses OpenAI-compatible format
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from dotenv import load_dotenv
from data_gen import generate_live_signals
from langchain_groq import ChatGroq

load_dotenv()

# Define the State
class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    migration_status: str 
    last_error: str
    confidence: int

# Initialize Official Llama API
# We use ChatOpenAI but change the 'base_url' to Meta's endpoint
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    groq_api_key=os.getenv("GROQ_API_KEY")
)

# --- NODE 1: ANALYZE ---
def analyze_issue(state: AgentState):
    prompt = f"""
    You are an AI Support Engineer for a SaaS platform.
    
    SYSTEM CONTEXT:
    - Migration Stage: {state['migration_status']}
    - Error Signal: {state['last_error']}
    
    TASK:
    Analyze if the merchant's issue is a result of the Hosted-to-Headless migration.
    Provide a clear reasoning for the support team.
    """
    response = llm.invoke(state['messages'] + [("system", prompt)])
    return {"messages": [response], "confidence": 95}

# --- NODE 2: ACT ---
def execute_action(state: AgentState):
    return {"messages": [("assistant", "ACTION: Recommending immediate rollback of API keys and alerting the migration team.")]}

def verify_fix(state: AgentState):
    """
    The Learning Phase: Did the action actually fix the problem?
    """
    # Simulate a post-action observation
    # In a real app, you would re-run generate_live_signals() here
    success = False # Let's simulate a failure to show the rollback!
    
    if not success:
        return {
            "messages": [("assistant", "⚠️ Error persists after fix. INITIATING ROLLBACK to previous configuration.")],
            "confidence": 0
        }
    else:
        return {"messages": [("assistant", "✅ Fix verified. System stable. Learning: This solution works for Webhook mismatches.")]}

# --- BUILD THE GRAPH ---
builder = StateGraph(AgentState)
builder.add_node("analyzer", analyze_issue)
builder.add_node("actor", execute_action)
builder.add_node("verifier", verify_fix) # New Node

builder.add_edge(START, "analyzer")
builder.add_edge("analyzer", "actor")
builder.add_edge("actor", "verifier") # Check after acting
builder.add_edge("verifier", END)

agent_app = builder.compile()


# --- RUN THE CYCLE ---
def run_agent_cycle():
    # Observe
    merchants, logs, tickets = generate_live_signals()
    problem_log = logs[0] 
    merchant_info = next(m for m in merchants if m['id'] == problem_log['merchant_id'])
    
    # Ingest
    initial_state = {
        "messages": [("user", f"Ticket: {tickets[0]['text']}")],
        "migration_status": merchant_info['stage'], 
        "last_error": problem_log['event'],        
        "confidence": 0 
    }

    print(f"--- [OBSERVE] Analyzing {merchant_info['name']} via Official Llama API ---")
    
    # Reason & Act
    final_state = agent_app.invoke(initial_state)
    
    print(f"\n--- LLAMA'S REASONING ---\n{final_state['messages'][-2].content}")
    print(f"\n--- DECISION ---\n{final_state['messages'][-1].content}")

if __name__ == "__main__":
    run_agent_cycle()