import os
from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from dotenv import load_dotenv
from data_gen import generate_live_signals
from langchain_groq import ChatGroq

load_dotenv()

# --- 1. DEFINE THE STATE ---
class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    migration_status: str 
    last_error: str
    confidence: int
    risk_level: str   # Added for Triage
    action_type: str  # Added for Triage

# Initialize Groq Llama 3
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    groq_api_key=os.getenv("GROQ_API_KEY")
)

# --- NODE 1: ANALYZE ---
import re

def analyze_issue(state: AgentState):
    prompt = f"""
    You are a Senior 'Self-Healing' Support Engineer. 
    
    --- RAW INVESTIGATION DATA ---
    MERCHANT CONTEXT: {state['migration_status']}
    TECHNICAL ERROR: {state['last_error']}
    
    --- YOUR MISSION ---
    1. DIAGNOSE: Compare the merchant's status with the error. 
    2. CLASSIFY: Is this a 'Migration Gap' (Headless move) or 'Legacy Platform' issue?
    3. ASSESS CONFIDENCE: Based on the alignment of the Merchant Status and the Technical Error, how certain are you of this diagnosis? 
       - If they match perfectly (e.g., Headless + Webhook Mismatch), confidence is 95-99%.
       - If it's a generic error (e.g., Server Timeout), confidence is 80-85%.
       - If the signals are contradictory, confidence is below 70%.

    --- OUTPUT FORMAT ---
    You must end your response with: "CONFIDENCE_SCORE: X" (where X is a number).
    
    --- STYLE ---
    - Use 'Based on the pattern of...'
    - Be professional and direct.
    """
    
    response = llm.invoke(state['messages'] + [("system", prompt)])
    content = response.content

    # Extract the number from the LLM's text using regex
    # If it fails to find a number, it defaults to 85
    match = re.search(r"CONFIDENCE_SCORE:\s*(\d+)", content)
    conf_score = int(match.group(1)) if match else 85
    
    # Clean up the message so the "CONFIDENCE_SCORE: X" doesn't show in the UI
    clean_content = re.sub(r"CONFIDENCE_SCORE:\s*\d+", "", content).strip()
    response.content = clean_content

    return {"messages": [response], "confidence": conf_score}

# --- NODE 2: ACT (Risk-Based Triage) ---
def execute_action(state: AgentState):
    last_error = state.get('last_error', 'Unknown')
    
    # Logic-based Triage mapping to your specific UI requirements
    if "Mismatch" in last_error or "Signature" in last_error:
        risk = "Low"
        message = "A minor configuration issue was detected and resolved automatically. Your migration continues as expected."
        action_type = "AUTO_FIX"
    elif "Timeout" in last_error:
        risk = "Medium"
        message = "We’re experiencing a temporary delay due to a third-party system. No action is required from you."
        action_type = "DELAY_NOTICE"
    else:
        risk = "High"
        message = "We detected an issue that may affect data integrity. Our engineers are actively investigating."
        action_type = "HUMAN_APPROVAL_REQUIRED"

    return {
        "messages": [("assistant", message)], 
        "risk_level": risk,
        "action_type": action_type
    }

# --- NODE 3: VERIFY ---
def verify_fix(state: AgentState):
    # For demo purposes, we simulate success for Low/Medium, and pause for High
    risk = state.get('risk_level', 'Low')
    if risk == "High":
        return {"messages": [("assistant", "⚠️ System paused. Awaiting manual override for data safety.")]}
    
    return {"messages": [("assistant", "✅ Fix verified. System heartbeat stable.")]}

# --- BUILD THE GRAPH ---
builder = StateGraph(AgentState)
builder.add_node("analyzer", analyze_issue)
builder.add_node("actor", execute_action)
builder.add_node("verifier", verify_fix)

builder.add_edge(START, "analyzer")
builder.add_edge("analyzer", "actor")
builder.add_edge("actor", "verifier")
builder.add_edge("verifier", END)

agent_app = builder.compile()

# --- RUN THE CYCLE (For Terminal Testing) ---
def run_agent_cycle():
    merchants, tickets = generate_live_signals()
    # Simulate first ticket
    tkt = tickets[0]
    
    initial_state = {
        "messages": [("user", tkt['desc'])],
        "migration_status": "Headless", 
        "last_error": tkt['issue'],        
        "confidence": 0 
    }

    print(f"--- [OBSERVE] Analyzing Issue: {tkt['issue']} ---")
    final_state = agent_app.invoke(initial_state)
    
    print(f"\n--- REASONING ---\n{final_state['messages'][-3].content}")
    print(f"\n--- TRIAGE ---\nRisk: {final_state['risk_level']}")
    print(f"\n--- FINAL MESSAGE ---\n{final_state['messages'][-2].content}")

if __name__ == "__main__":
    run_agent_cycle()