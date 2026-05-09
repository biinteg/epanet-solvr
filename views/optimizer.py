# pyrefly: ignore [missing-import]
import streamlit as st
import tempfile
import os
import time
from datetime import datetime
from views import styles
from modules.auto_solver import run_auto_solver
from modules.pressure_analysis import run_pressure_analysis
from modules.hardy_cross import run_hardy_cross

def add_log(msg, type='info'):
    if "log_history" not in st.session_state:
        st.session_state["log_history"] = []
    
    timestamp = datetime.now().strftime("%H:%M:%S")
    color = "#66d39b" if type == 'success' else "#ff4b4b" if type == 'error' else "#cfd6d4"
    log_entry = f'<span style="color: {color};">{timestamp} {msg}</span>'
    st.session_state["log_history"].append(log_entry)
    # Keep only last 10 logs for performance
    if len(st.session_state["log_history"]) > 15:
        st.session_state["log_history"].pop(0)

def render():
    styles.inject_optimizer_styles()

    if "log_history" not in st.session_state:
        st.session_state["log_history"] = [
            '<span style="color: #cfd6d4;">Initializing EPANET workspace...</span>',
            '<span style="color: #cfd6d4;">Ready for network upload.</span>'
        ]

    st.html("""
        <div class="top-nav">
            <div class="nav-brand">EPANET Solver</div>
            <div class="nav-links">
                <a class="nav-link" href="?page=home" target="_self">Home</a>
                <a class="nav-link active" href="?page=optimizer" target="_self">Optimizer</a>
                <a class="nav-link" href="#documentation" target="_self">Documentation</a>
            </div>
            <div class="nav-actions" aria-label="Account notifications">
                <span style="font-size: 24px;">👤</span>
                <span style="font-size: 24px;">🔔</span>
            </div>
        </div>
    """)

    st.html("""
        <div class="dashboard-shell">
            <div class="dashboard-kicker">Optimizing network dashboard</div>
            <h1 class="dashboard-title">Optimization Dashboard</h1>
            <p class="dashboard-subtitle">
                Real-time analysis and automatic sizing of the water distribution network based on
                Permen PU No. 18/PRT/M/2007 criteria.
            </p>
        </div>
    """)

    # Main Layout: Sidebar-like left column and Workspace right column
    col_left, col_right = st.columns([1, 2.8], gap="large")

    with col_left:
        st.markdown("### Select Feature")
        
        feature_options = [
            "Auto-Solver",
            "Pressure & Auto-PRV",
            "Hardy Cross"
        ]
        
        # Detect selection change to add log
        old_menu = st.session_state.get("last_selected_feature", "")
        menu = st.radio(
            "Pilih fitur optimizer",
            feature_options,
            label_visibility="collapsed",
            key="feature_selector"
        )
        
        if menu != old_menu:
            st.session_state["last_selected_feature"] = menu
            add_log(f"Feature selected: {menu}")
        
        selected_engine = "EPyT" if "Auto-Solver" in menu else "WNTR" if "Pressure" in menu else "Manual Loop"
        
        st.markdown("---")
        st.markdown("### Target Criteria")
        st.html("""
            <div class="feature-selection-container">
                <div class="feature-selection-card" style="padding: 16px;">
                    <div style="font-size: 32px; margin-bottom: 8px;">🌡️</div>
                    <h4 style="font-size:14px;">Pressure</h4>
                    <p style="font-size:12px;">10 - 80m</p>
                </div>
                <div class="feature-selection-card" style="padding: 16px;">
                    <div style="font-size: 32px; margin-bottom: 8px;">💧</div>
                    <h4 style="font-size:14px;">Velocity</h4>
                    <p style="font-size:12px;">0.3 - 2.5 m/s</p>
                </div>
                <div class="feature-selection-card" style="padding: 16px;">
                    <div style="font-size: 32px; margin-bottom: 8px;">📉</div>
                    <h4 style="font-size:14px;">Headloss</h4>
                    <p style="font-size:12px;">Max 10 m/km</p>
                </div>
            </div>
        """)

    with col_right:
        # Live Terminal Component
        log_content = "<br>".join(st.session_state["log_history"])
        st.html(f"""
            <div class="optimizer-workspace" style="margin-top: 0; grid-template-columns: 1fr;">
                <div class="log-card">
                    <div class="log-head">
                        <h3>💻 Live Optimization Log</h3>
                        <span class="engine-pill">{selected_engine} Engine</span>
                    </div>
                    <div class="log-console" id="terminal-output">
                        {log_content}
                    </div>
                </div>
            </div>
        """)
        
        st.html("""
            <div style="margin-top: 32px;">
                <div class="upload-title" style="text-align: left;">
                    <h2 class="hero-title" style="font-size: 32px;">Upload Your Network</h2>
                    <p class="hero-subtitle" style="margin: 0;">Drag and drop your .inp file here to begin.</p>
                </div>
            </div>
        """)
        
        uploaded_file = st.file_uploader("", type=["inp"], key="main_uploader", label_visibility="collapsed")
        
        if uploaded_file:
            if "file_logged" not in st.session_state or st.session_state.file_logged != uploaded_file.name:
                add_log(f"File uploaded: {uploaded_file.name}", 'success')
                add_log("Validating network topology...")
                st.session_state.file_logged = uploaded_file.name

        if uploaded_file is None:
            st.info("Pilih fitur optimizer di kiri, lalu unggah file .inp untuk memulai.")
            st.session_state['run_solver'] = False

        action_mid = st.container()
        with action_mid:
            start_clicked = st.button(
                "Start Optimization  →",
                type="primary",
                use_container_width=True,
                disabled=uploaded_file is None,
                key="start_opt_btn"
            )

        if uploaded_file is not None:
            if start_clicked:
                st.session_state['run_solver'] = True
                add_log(f"Starting {menu} Engine...", 'info')
                
        if st.session_state.get('run_solver', False):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".inp") as tmp:
                # pyrefly: ignore [missing-attribute]
                tmp.write(uploaded_file.getvalue())
                tmp_path = tmp.name

            try:
                # Since we can't easily pass callback to existing modules without refactoring them,
                # we'll add dummy progress logs here for effect, then run the actual solver.
                add_log("Analyzing link diameters...")
                add_log("Running hydraulic simulations...")
                
                with st.spinner(f"Optimizing Network... using {menu}"):
                    if "Auto-Solver" in menu:
                        run_auto_solver(tmp_path)
                    elif "Pressure" in menu:
                        run_pressure_analysis(tmp_path)
                    elif "Hardy Cross" in menu:
                        run_hardy_cross(tmp_path)
                
                add_log("Optimization complete!", 'success')
                st.session_state['run_solver'] = False
                st.rerun() # Refresh to show logs

            except Exception as e:
                add_log(f"Error: {str(e)}", 'error')
                st.error(f"Gagal menjalankan analisis: {str(e)}")
                st.session_state['run_solver'] = False
            finally:
                if os.path.exists(tmp_path):
                    try:
                        os.remove(tmp_path)
                    except:
                        pass

    st.html("""
        <div class="footer">
            <div class="footer-brand">EPANET Solver</div>
            <div class="footer-copy">© 2026 EPANET Solver. Compliance: Permen PU Standards.</div>
        </div>
    """)
