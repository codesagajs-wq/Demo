import streamlit as st
import requests
import json
from datetime import datetime

st.set_page_config(
    page_title="Back Office Automated Report Generator and Workflow Coordinator",
    layout="wide",
    initial_sidebar_state="expanded"
)

API_URL = "http://localhost:8000"
HEALTH_PATH = "/health"
REPORT_PATH = "/api/reports/query"
TOKEN_PATH = "/token"
USER_ME_PATH = "/api/user/me"


def backend_health():
    try:
        r = requests.get(f"{API_URL}{HEALTH_PATH}", timeout=3)
        return r.status_code == 200, r.text
    except Exception as e:
        return False, str(e)

def call_generate_report(query: str, token: str):
    """Call backend report endpoint and return (ok, status_code, body_or_error)."""
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    try:
        resp = requests.post(
            f"{API_URL}{REPORT_PATH}",
            json={"query": query},
            headers=headers,
            timeout=120
        )
        return True, resp.status_code, resp.text
    except requests.exceptions.RequestException as e:
        return False, None, str(e)

def try_login(username: str, password: str):
    try:
        r = requests.post(f"{API_URL}{TOKEN_PATH}", data={"username": username, "password": password}, timeout=10)
        if r.status_code == 200:
            data = r.json()
            return True, data.get("access_token"), None
        else:
            return False, None, f"{r.status_code} {r.text}"
    except Exception as e:
        return False, None, str(e)


if "token" not in st.session_state:
    st.session_state.token = None
if "user" not in st.session_state:
    st.session_state.user = None
if "report_generated" not in st.session_state:
    st.session_state.report_generated = False
if "result" not in st.session_state:
    st.session_state.result = None
if "running" not in st.session_state:
    st.session_state.running = False
if "example_query" not in st.session_state:
    st.session_state.example_query   = ""


st.markdown(
    """
    <style>
        .main-header {
            font-size: 2.2rem;
            font-weight: 700;
            margin-bottom: 0.3rem;
        }
        .query-box {
            background: #f8f9fa;
            padding: 18px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }
    </style>
    """,
    unsafe_allow_html=True,
)



def do_logout():
    st.session_state.token = None
    st.session_state.user = None
    st.session_state.report_generated = False
    st.session_state.result = None

def fetch_current_user(token: str):
    try:
        r = requests.get(f"{API_URL}{USER_ME_PATH}", headers={"Authorization": f"Bearer {token}"}, timeout=5)
        if r.status_code == 200:
            return True, r.json()
        else:
            return False, f"{r.status_code} {r.text}"
    except Exception as e:
        return False, str(e)


if not st.session_state.token:
    st.html("""
        <h1 style="margin-bottom: 0;">
            Back Office Automated Report Generator and Workflow Coordinator
        </h1>
        """)
    st.html("""
            <h2 style="margin: 5px;">
        Login
            </h2>
        """)


    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            username = st.text_input("Email", placeholder="user@tcs.com")
            password = st.text_input("Password", type="password", placeholder="Enter password")
            submitted = st.form_submit_button("Login", use_container_width=True)
            if submitted:
                ok, token, err = try_login(username, password)
                if ok and token:
                    st.session_state.token = token
                    ok_user, user_or_err = fetch_current_user(token)
                    if ok_user:
                        st.session_state.user = user_or_err
                        st.success("Login successful!")
                        # reload to show main UI (safe)
                        st.rerun()
                    else:
                        st.error(f"Failed to fetch user info: {user_or_err}")
                else:
                    st.error(f"Login failed: {err}")

    st.stop()  # stop further rendering until logged in

col1, col2 = st.columns([7, 1])
with col1:
    st.html("""
        <h1 style="margin-bottom: 0;">
            Back Office Automated Report Generator and Workflow Coordinator
        </h1>
        """)

with col2:
    try:
        user_display = st.session_state.user.get("full_name", "Unknown")
        role = st.session_state.user.get("role", "")
        dept = st.session_state.user.get("department", "")
    except Exception:
        user_display = "Unknown"
        role = dept = ""
    st.markdown(f"**👤 {user_display}**")
    st.caption(f"{role} - {dept}")
    if st.button("Logout"):
        do_logout()
        st.rerun()

st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("ℹHow It Works")
    st.markdown(
        """
        **1. Ask in Natural Language** — Type the business question you want answered.

        **2. AI Understands & Plans** — The system parses intent, picks data sources and builds an approval workflow.

        **3. Fetches & Analyzes** — Gets ERP/CRM data, runs analytics and forecasts.

        **4. Generates Report** — Final human-readable report + downloadable JSON.
        """
    )
    st.markdown("---")
    st.subheader("Example Queries")
    examples = [
        "Show me Q3 sales performance",
        "Financial report for last 6 months",
        "Top performing customers in technology sector",
        "Sales by region with forecasts",
        "Urgent financial analysis needed",
        "Compare sales performance across products",
        "CRM pipeline report for this quarter",
        "Transaction analysis for pending orders"
    ]
    for ex in examples:
        if st.button(ex, key=f"ex_{ex}"):
            st.session_state.example_query = ex
            st.rerun()

with st.container():
    st.markdown("### Enter Your Query to Generate Back-Office Report")

    print(st.session_state.example_query)
    with st.form("generate_form"):
        user_query = st.text_area(
            "Type your query here...",
            value=st.session_state.example_query,
            height=120,
            placeholder="Example: Show me sales performance for Q3 with regional breakdown and forecasts"
        )

        col1, col2 = st.columns([.85, .15])
        with col1:
            submit_generate = st.form_submit_button("Generate Report")
        with col2:
            if st.form_submit_button("Clear (Reset)"):
                st.session_state.pop("example_query", "")
                st.session_state.report_generated = False
                st.session_state.result = None
                st.rerun()

if submit_generate:
    if not user_query or not user_query.strip():
        st.error("Please enter a query.")
    else:
        if st.session_state.running:
            st.info("A request is already running. Please wait.")
        else:
            st.session_state.running = True
            try:
                with st.spinner("Processing your query and generating report..."):
                    progress = st.progress(0)
                    status_text = st.empty()

                    status_text.text("Parsing your query...")
                    progress.progress(10)

                    ok_health, _ = backend_health()
                    if not ok_health:
                        st.error("Backend is currently unreachable. Please check backend service.")
                        st.session_state.running = False
                    else:
                        status_text.text("Contacting backend report service...")
                        progress.progress(25)

                        ok_call, code, body = call_generate_report(user_query, st.session_state.token)
                
                        st.debug_text = f"DBG: ok_call={ok_call}, code={code}"  # intentionally set for debugging display below
                        progress.progress(50)
                        status_text.text("Generating final report...")

                        if not ok_call:
                            st.error(f"Network error: {body}")
                        else:
                            
                            progress.progress(80)
                            
                            # show status & body for visibility, then parse if 200
                            status_text.text(f"Backend responded [{code}]")
                            st.write("DEBUG RESPONSE (backend):", code)
                            st.write(body)

                            if code == 200:
                                try:
                                    result_json = json.loads(body)
                                except Exception:
                                    st.error("Backend returned non-JSON response.")
                                    result_json = {"report": body}


                                status_text.text("")
                                progress.progress(100)

                                st.session_state.result = result_json
                                st.session_state.report_generated = True
            
                                st.success("Report generated successfully!")
                            elif code == 401:
                                st.error("Authentication error (401). Please login again.")
                                # clear token / force re-login
                                do_logout()
                            else:
                                # show response text for debugging
                                st.error(f"Backend returned status {code}. See debug below.")
                                st.write(body)

                        progress.progress(100)
            except Exception as e:
                st.error(f"Unexpected error: {str(e)}")
            finally:
                st.session_state.running = False

if st.session_state.report_generated and st.session_state.result:
    result = st.session_state.result

    st.markdown("---")
    st.subheader("Report Priority and Value Overview")
    parsed = result.get("parsed_request", {})

    col1, col2, col3 = st.columns(3)
    col1.metric("Report Type", parsed.get("report_type", "N/A").upper())
    col2.metric("Urgency", parsed.get("urgency", "N/A").upper())
    col3.metric("Value Impact", parsed.get("value_impact", "N/A").upper())

    with st.expander("Parsed Request Details", expanded=False):
        st.write("**Interpretation:**", parsed.get("interpretation", "N/A"))
        st.write("**Report Focus:**", parsed.get("report_focus", "N/A"))
        st.write("**Data Sources:**", ", ".join(parsed.get("data_sources", [])))
        if parsed.get("filters"):
            st.write("**Filters Applied:**")
            for k, v in parsed.get("filters", {}).items():
                if v:
                    st.write(f"- {k}: {v}")

    st.subheader("Data Sources Used")
    records = result.get("records_fetched", {})
    if not records:
        st.info("No records info returned from backend.")
    else:
        cols = st.columns(max(1, len(records)))
        for i, (source, count) in enumerate(records.items()):
            with cols[i]:
                st.metric(source.replace("_", " ").title(), f"{count} records")

    st.markdown("---")
    st.subheader("Approval Workflow for the report")
    workflow = result.get("workflow", {})
    col1, col2 = st.columns([3, 1])
    with col1:
        st.info(f"**{workflow.get('name', 'N/A')}**")
        if workflow.get("reason"):
            st.caption(f"{workflow['reason']}")
        stages = workflow.get("stages", [])
        for i, stage in enumerate(stages, 1):
            with st.expander(f"Stage {i}: {stage.get('name', 'Unknown')}", expanded=True):
                st.write(f"**Approvers:** {', '.join(stage.get('approvers', []))}")
                st.write(f"**Type:** {stage.get('type', 'N/A')}")
                st.write(f"**Requires:** {stage.get('requires', 'N/A')}")
                st.write(f"**Timeout:** {stage.get('timeout_hours', 0)} hours")

    with col2:
        st.metric("Total Stages", len(stages))
        st.metric("Status", workflow.get("status", "N/A").upper())

    st.markdown("---")
    st.subheader("Predictive Analytics & Insights")

    tab1, tab2, tab3, tab4 = st.tabs(["Insights", "Anomalies", "Forecasts", "Data Summary"])

    with tab1:
        insights = result.get("insights", [])
        if insights:
            for ins in insights:
                st.success(f"--> {ins}")
        else:
            st.info("No insights generated")

    with tab2:
        anomalies = result.get("anomalies", [])
        if anomalies:
            for a in anomalies:
                sev = a.get("severity", "low")
                level = {"low": st.info, "medium": st.warning, "high": st.error}.get(sev, st.info)
                level(f"**{a.get('type','Unknown')}:** {a.get('message','No message')}")
        else:
            st.success("No anomalies detected")

    with tab3:
        forecasts = result.get("forecasts", {})
        if forecasts:
            st.json(forecasts)
        else:
            st.info("No forecasts available")

    with tab4:
        aggregated = result.get("aggregated_data", {})
        if aggregated:
            st.json(aggregated)
        else:
            st.info("No aggregated data")

    st.markdown("---")
    st.subheader("Generated Report")
    with st.expander("View Full Report", expanded=True):
        st.markdown(result.get("report", "No report generated"))

    col1, col2, col3 = st.columns(3)
    with col1:
        st.download_button(
            "Download Report (TXT)",
            result.get("report", ""),
            file_name=f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain",
            use_container_width=True
        )
    with col2:
        st.download_button(
            "Download Workflow (JSON)",
            json.dumps(result.get("workflow", {}), indent=2),
            file_name="workflow_config.json",
            mime="application/json",
            use_container_width=True
        )
    with col3:
        st.download_button(
            "Download Full Results (JSON)",
            json.dumps(result, indent=2, default=str),
            file_name="full_report_data.json",
            mime="application/json",
            use_container_width=True
        )

st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray;'>
        <p>TCS AI Fridays Hackathon 2025 | Back Office Automated Report Generator and Workflow Coordinator</p>
    </div>
    """,
    unsafe_allow_html=True,
)
