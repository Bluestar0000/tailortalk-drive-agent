import os
import requests
import streamlit as st

BACKEND = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(
    page_title="TailorTalk Drive Agent",
    page_icon="🗂️",
    layout="wide",
)
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
#MainMenu, footer, header { visibility: hidden; }

.metric-card {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 16px 20px;
    text-align: center;
}
.metric-value { font-size: 1.8rem; font-weight: 600; color: #1e293b; }
.metric-label { font-size: 0.78rem; color: #64748b; margin-top: 2px; }

.file-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 12px 16px;
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    gap: 12px;
}
.query-badge {
    background: #eff6ff;
    border: 1px solid #bfdbfe;
    border-radius: 6px;
    padding: 6px 12px;
    font-family: monospace;
    font-size: 0.8rem;
    color: #1d4ed8;
    margin-top: 6px;
    word-break: break-all;
}
.success-badge {
    background: #f0fdf4;
    color: #16a34a;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 0.75rem;
    font-weight: 500;
}
.fail-badge {
    background: #fef2f2;
    color: #dc2626;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 0.75rem;
    font-weight: 500;
}
.speed-badge {
    background: #fafafa;
    border: 1px solid #e5e7eb;
    color: #6b7280;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 0.75rem;
}
</style>
""", unsafe_allow_html=True)
if "messages" not in st.session_state:
    st.session_state.messages = []

st.markdown("## 🗂️ TailorTalk Drive Agent")
st.caption("Conversational file discovery powered by LLM + Google Drive API")
st.divider()
chat_col, metrics_col = st.columns([2, 1], gap="large")

with metrics_col:
    st.markdown("#### 📊 Session Analytics")

    try:
        m = requests.get(f"{BACKEND}/metrics", timeout=3).json()

        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{m['total_queries']}</div>
                <div class="metric-label">Total Queries</div>
            </div>""", unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{m['success_rate']}%</div>
                <div class="metric-label">Success Rate</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        c3, c4 = st.columns(2)
        with c3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{int(m['avg_response_time_ms'])}ms</div>
                <div class="metric-label">Avg Response</div>
            </div>""", unsafe_allow_html=True)
        with c4:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{m['successful_queries']}</div>
                <div class="metric-label">Successful</div>
            </div>""", unsafe_allow_html=True)

    except Exception:
        st.warning("Backend offline")

    st.divider()

    st.markdown("####  Query History")
    try:
        log = m.get("query_log", [])
        if log:
            for entry in reversed(log[-8:]):
                badge = '<span class="success-badge">✓</span>' if entry["success"] else '<span class="fail-badge">✗</span>'
                speed = f'<span class="speed-badge">{entry["response_time_ms"]}ms</span>'
                st.markdown(
                    f'{badge} {speed} &nbsp; <small>{entry["query"][:35]}{"..." if len(entry["query"]) > 35 else ""}</small>',
                    unsafe_allow_html=True
                )
                st.markdown("<div style='margin:4px'></div>", unsafe_allow_html=True)
        else:
            st.caption("No queries yet")
    except Exception:
        st.caption("No data")

    st.divider()

    st.markdown("#### 💡 Try these")
    examples = [
        "List all files",
        "Find all images",
        "Show Google Docs",
        "Files modified this month",
        "Search for invoice",
    ]
    for ex in examples:
        if st.button(ex, use_container_width=True, key=f"ex_{ex}"):
            st.session_state["prefill"] = ex

    if st.button("🗑️ Clear chat", use_container_width=True):
        st.session_state.messages = []
        try:
            requests.delete(f"{BACKEND}/chat")
        except Exception:
            pass
        st.rerun()

with chat_col:
    st.markdown("#### 💬 Chat")
    if not st.session_state.messages:
        st.info("👋 Ask me to find files in your Google Drive. Try: *'List all files'* or *'Find images'*")
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("response_time_ms"):
                st.caption(f"⚡ {msg['response_time_ms']}ms")
    prefill = st.session_state.pop("prefill", "")
    user_input = st.chat_input("Ask me to find files...") or prefill

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Searching Drive..."):
                try:
                    res = requests.post(
                        f"{BACKEND}/chat",
                        json={"message": user_input},
                        timeout=30,
                    )
                    data = res.json()
                    reply = data.get("response", "Something went wrong.")
                    response_time = data.get("response_time_ms", 0)
                    success = data.get("success", False)
                except Exception as e:
                    reply = f"Could not reach backend: {str(e)}"
                    response_time = 0
                    success = False

            st.markdown(reply)
            st.caption(f"⚡ {response_time}ms")

        st.session_state.messages.append({
            "role": "assistant",
            "content": reply,
            "response_time_ms": response_time,
            "success": success,
        })

        st.rerun()