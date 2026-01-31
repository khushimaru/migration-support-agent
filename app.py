import streamlit as st
from agent import agent_app
from data_gen import generate_live_signals

st.set_page_config(page_title="Agentic Support Dashboard", layout="wide")
st.title("🛡️ SaaS Migration: Self-Healing Support Layer")

# --- 1. OBSERVE (Side Bar) ---
st.sidebar.header("📡 Live System Observer")
merchants, logs, tickets = generate_live_signals()

# Focus on the 'broken' merchant for the demo
problem_merchant = next(m for m in merchants if m['id'] == 103)
latest_log = [l for l in logs if l['merchant_id'] == 103][0]

st.sidebar.subheader("Merchant Context")
st.sidebar.json(problem_merchant)
st.sidebar.subheader("Live Error Log")
st.sidebar.error(f"Event: {latest_log['event']}")

# --- 2. REASON (Main Panel) ---
st.subheader("📥 Incoming Signal")
with st.chat_message("user"):
    st.write(f"**Ticket:** {tickets[0]['text']}")

if st.button("🧠 Invoke Agent Reasoning"):
    # Build the initial state for the agent
    initial_state = {
        "messages": [("user", tickets[0]['text'])],
        "migration_status": problem_merchant['stage'],
        "last_error": latest_log['event'],
        "confidence": 0
    }

    with st.spinner("Llama is analyzing patterns..."):
        # Run the agent
        result = agent_app.invoke(initial_state)
    
    # Store result in session state for the 'Act' step
    st.session_state.agent_result = result
    st.session_state.reasoning_complete = True

# --- 3. DECIDE & ACT (Human-in-the-Loop) ---
if st.session_state.get("reasoning_complete"):
    res = st.session_state.agent_result
    
    st.divider()
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🔍 Agent Reasoning & Root Cause")
        # Display the explanation from the analyzer node
        st.info(res['messages'][-2].content)
        
    with col2:
        st.subheader("⚖️ Operational Guardrails")
        confidence = res.get('confidence', 0)
        st.metric("Confidence Score", f"{confidence}%")
        
        # Ethical/Safety logic check
        if confidence < 90:
            st.error("⚠️ LOW CONFIDENCE: Manual Engineering review required.")
        else:
            st.success("✅ HIGH CONFIDENCE: Automated fix recommended.")

    # THE ACT STEP (Human Gate)
    st.subheader("🛠️ Proposed Action")
    action_text = res['messages'][-1].content
    st.code(action_text, language="markdown")
    
    st.warning("Decision Policy: This action affects live merchant data. Please confirm.")
    if st.button("Confirm & Execute Action"):
        st.balloons()
        st.success("Action Executed: System state updated and merchant notified.")