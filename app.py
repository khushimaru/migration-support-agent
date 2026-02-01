import streamlit as st
import time
from datetime import datetime
from agent import agent_app
from data_gen import generate_live_signals

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="AEGIS: Migration Guard",
    layout="wide",
    page_icon="🛡️"
)

# =========================================================
# GLOBAL DARK THEME (DARKPAN INSPIRED)
# =========================================================
st.markdown("""
<style>
html, body, [class*="css"] {
    background-color: #0b0d10 !important;
    color: #e6e6e6;
    font-family: Inter, system-ui, sans-serif;
}

.block-container {
    padding-top: 1.5rem;
    padding-bottom: 2rem;
}

h1, h2, h3, h4 {
    color: #f5f5f5;
    font-weight: 600;
}

/* Tabs */
.stTabs [data-baseweb="tab"] {
    background-color: #0f1218;
    color: #b5b5b5;
    border-radius: 10px;
    padding: 10px 18px;
    border: 1px solid #1f2430;
}

.stTabs [aria-selected="true"] {
    background-color: rgba(225, 6, 0, 0.15);
    color: #ffffff;
    border: 1px solid #e10600;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #e10600, #9b1c1c);
    color: white;
    border: none;
    border-radius: 12px;
    padding: 0.65rem 1.3rem;
    font-weight: 600;
}

.stButton > button:hover {
    background: linear-gradient(135deg, #ff2a2a, #b32020);
    transform: translateY(-1px);
}

/* Panels */
.stMarkdown, .stJson {
    background-color: #12151b;
    border: 1px solid #1f2430;
    border-radius: 12px;
}

/* Alerts */
.stAlert {
    background-color: #12151b;
    border-left: 6px solid #e10600;
}

hr {
    border-color: #1f2430;
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# STATE INITIALIZATION
# =========================================================
if "ticket_queue" not in st.session_state:
    merchants, raw_tickets = generate_live_signals()
    st.session_state.ticket_queue = raw_tickets.copy()
    st.session_state.merchants = merchants

if "metrics" not in st.session_state:
    st.session_state.metrics = {
        "Low": 0,
        "Medium": 0,
        "High": 0,
        "Affected_Merchants": set()
    }

if "history_log" not in st.session_state:
    st.session_state.history_log = []

# =========================================================
# HEADER
# =========================================================
st.markdown("""
<h1 style="letter-spacing:1px;">
<span style="color:#e10600;">AEGIS</span> Migration Guard
</h1>
<p style="color:#888; margin-top:-10px;">
Autonomous Support & Self-Healing Infrastructure for SaaS Platforms
</p>
""", unsafe_allow_html=True)

# =========================================================
# TABS
# =========================================================
tab_metrics, tab_investigation, tab_audit = st.tabs([
    "Executive Summary",
    "Live Investigation",
    "System Audit"
])

# =========================================================
# METRIC CARD COMPONENT
# =========================================================
def metric_card(title, value, color):
    return f"""
<div style="
    background: linear-gradient(180deg, #141821, #0f1218);
    border: 1px solid {color};
    border-radius: 14px;
    padding: 22px;
    text-align: center;
    box-shadow: 0 0 24px rgba(0,0,0,0.5);
">
    <div style="color:#999; font-size:0.8rem; letter-spacing:1px;">
        {title.upper()}
    </div>
    <div style="color:{color}; font-size:2.6rem; font-weight:700; margin-top:6px;">
        {value}
    </div>
</div>
"""

# =========================================================
# TAB 1 — EXECUTIVE SUMMARY
# =========================================================
with tab_metrics:
    st.subheader("Platform Health Overview")
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown(metric_card("Low Risk", st.session_state.metrics["Low"], "#2ecc71"), unsafe_allow_html=True)
    with c2:
        st.markdown(metric_card("Medium Risk", st.session_state.metrics["Medium"], "#f39c12"), unsafe_allow_html=True)
    with c3:
        st.markdown(metric_card("High Risk", st.session_state.metrics["High"], "#e10600"), unsafe_allow_html=True)
    with c4:
        st.markdown(metric_card(
            "Merchants Affected",
            len(st.session_state.metrics["Affected_Merchants"]),
            "#ff3b3b"
        ), unsafe_allow_html=True)

# =========================================================
# TAB 2 — LIVE INVESTIGATION
# =========================================================
with tab_investigation:
    if st.session_state.ticket_queue:
        current_ticket = st.session_state.ticket_queue[0]
        st.info(f"**Active Signal:** Investigating Incident `{current_ticket['id']}`")

        left, right = st.columns(2)

        with left:
            st.markdown("#### [Observe] Incoming Signal")
            st.json(current_ticket)

        with right:
            st.markdown("#### [Reason & Decide]")
            if st.button("Invoke Agent Reasoning Engine", use_container_width=True):
                initial_state = {
                    "messages": [("user", current_ticket.get("desc", ""))],
                    "migration_status": "Headless",
                    "last_error": current_ticket["issue"],
                    "confidence": 0
                }

                with st.spinner("Llama 3.3 analyzing architecture & logs…"):
                    result = agent_app.invoke(initial_state)
                    st.session_state.current_result = result
                    st.session_state.current_risk = result.get("risk_level", "Low")
                    st.session_state.current_confidence = result.get("confidence", 70)

        if "current_result" in st.session_state:
            res = st.session_state.current_result
            risk = st.session_state.current_risk
            conf = st.session_state.current_confidence

            st.divider()
            st.markdown(f"**Agent Reasoning:** {res['messages'][-2].content}")
            st.metric("Reasoning Confidence", f"{conf}%")
            st.progress(conf / 100)

            # --- PATH A: AUTONOMOUS RESOLUTION (LOW / MEDIUM) ---
            if risk in ["Low", "Medium"]:
                st.write(f"⚙️ **Auto-Action:** System identified {risk} risk. Implementing self-healing resolution...")
                time.sleep(2)
                
                st.session_state.metrics[risk] += 1
                st.session_state.metrics["Affected_Merchants"].add(current_ticket["merchant_id"])
                st.session_state.history_log.append({
                    "id": current_ticket["id"],
                    "issue": current_ticket["issue"],
                    "risk": risk,
                    "action": f"Autonomous {risk}-Risk Mitigation Applied",
                    "time": datetime.now().strftime("[%H:%M:%S]")
                })
                
                st.session_state.ticket_queue.pop(0)
                del st.session_state.current_result
                st.rerun()

            # --- PATH B: HUMAN-IN-THE-LOOP (HIGH RISK ONLY) ---
            else:
                st.error("🛑 CRITICAL RISK DETECTED")
                st.warning("Ethics Protocol: Manual confirmation required for high-impact action.")
                
                st.markdown("### 🛠️ High-Risk Intervention")
                manual_col, agent_col = st.columns(2)
                
                with manual_col:
                    manual_mode = st.checkbox("🚫 No, I'll solve this on my own", key=f"manual_{current_ticket['id']}")

                if manual_mode:
                    st.info("💡 **Manual Mode Active:** Agent paused for human intervention.")
                    if st.button("✅ I have resolved this manually", type="primary", use_container_width=True):
                        st.session_state.history_log.append({
                            "id": current_ticket["id"],
                            "issue": current_ticket["issue"],
                            "risk": "High",
                            "action": "Manual Override: Resolved by User",
                            "time": datetime.now().strftime("[%H:%M:%S]")
                        })
                        st.session_state.ticket_queue.pop(0)
                        del st.session_state.current_result
                        st.rerun()
                else:
                    approve = st.checkbox("I approve the agent's proposed critical fix", key=f"approve_{current_ticket['id']}")
                    if st.button("🚀 Approve & Execute", disabled=not approve, type="primary", use_container_width=True):
                        st.session_state.metrics["High"] += 1
                        st.session_state.history_log.append({
                            "id": current_ticket["id"],
                            "issue": current_ticket["issue"],
                            "risk": "High",
                            "action": "Critical Fix (Human Approved)",
                            "time": datetime.now().strftime("[%H:%M:%S]")
                        })
                        st.session_state.ticket_queue.pop(0)
                        del st.session_state.current_result
                        st.balloons()
                        st.rerun()
    else:
        st.success("All signals clear. Passive monitoring active.")
        if st.button("Restart Simulation"):
            del st.session_state.ticket_queue
            st.rerun()

# =========================================================
# TAB 3 — SYSTEM AUDIT
# =========================================================
with tab_audit:
    st.subheader("System Event Log")

    if not st.session_state.history_log:
        st.info("No audit events recorded.")

    for item in reversed(st.session_state.history_log):
        if item["risk"] == "High":
            color, label, icon = "#e10600", "CRITICAL", "🚨"
        elif item["risk"] == "Medium":
            color, label, icon = "#f39c12", "WARNING", "🕒"
        else:
            color, label, icon = "#2ecc71", "LOW", "✅"

        st.markdown(f"""
        <div style="
            background-color:#0f1218;
            border-left:6px solid {color};
            border-radius:10px;
            padding:16px 18px;
            margin-bottom:14px;
            box-shadow: inset 0 0 0 1px #1f2430;
        ">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="font-family:monospace; color:#999; font-size:0.85rem;">{item['time']}</span>
                <span style="background:{color}; color:black; padding:2px 10px; border-radius:12px; font-size:0.7rem; font-weight:700;">{label}</span>
            </div>
            <div style="margin-top:12px; display:flex; gap:14px; align-items:center;">
                <div style="font-size:1.5rem;">{icon}</div>
                <div>
                    <div style="font-weight:600; color:#f5f5f5; font-size:1rem;">
                        Ticket {item['id']} — {item['issue']}
                    </div>
                    <div style="font-size:0.85rem; color:#888;">
                        ACTION: {item['action']}
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)