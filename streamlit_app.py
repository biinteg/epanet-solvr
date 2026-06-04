# streamlit_app.py
# pyrefly: ignore [missing-import]
import streamlit as st
from views import styles, landing, optimizer

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="EPANET Solver",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Inject Global Styles
styles.inject_global_css()

# =====================================================
# STATE MANAGEMENT & ROUTING
# =====================================================

if "app_started" not in st.session_state:
    st.session_state["app_started"] = False
if "run_solver" not in st.session_state:
    st.session_state["run_solver"] = False

# Simple routing based on query params
page_param = st.query_params.get("page", "")
if page_param == "optimizer":
    st.session_state["app_started"] = True
elif page_param == "home":
    st.session_state["app_started"] = False
    st.session_state["run_solver"] = False

# =====================================================
# VIEW RENDERING
# =====================================================

if not st.session_state["app_started"]:
    landing.render()
else:
    optimizer.render()
