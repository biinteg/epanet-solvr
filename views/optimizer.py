# pyrefly: ignore [missing-import]
import streamlit as st
import tempfile
import os
from views import styles
from modules.auto_solver import run_auto_solver
from modules.pressure_analysis import run_pressure_analysis
from modules.hardy_cross import run_hardy_cross

def render():
    styles.inject_optimizer_styles()

    st.html("""
        <div class="top-nav">
            <div class="nav-brand">EPANET Solver</div>
            <div class="nav-links">
                <a class="nav-link" href="?page=home" target="_self">Home</a>
                <a class="nav-link active" href="?page=optimizer" target="_self">Optimizer</a>
                <a class="nav-link" href="#documentation" target="_self">Documentation</a>
            </div>
            <div class="nav-actions" aria-label="Account notifications">
                <span class="material-symbols-outlined">account_circle</span>
                <span class="material-symbols-outlined">notifications</span>
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
            "Auto-Solver (Engine: EPyT)",
            "Pressure & Auto-PRV (Engine: WNTR)",
            "Hardy Cross (Manual Loop)"
        ]
        
        # Use a hidden radio but styled cards
        # For simplicity and interactivity, we'll use a standard radio for now but on the left
        menu = st.radio(
            "Pilih fitur optimizer",
            feature_options,
            label_visibility="collapsed"
        )
        
        selected_engine = "EPyT" if "EPyT" in menu else "WNTR" if "WNTR" in menu else "Manual Loop"
        
        st.html(f"""
            <div class="feature-selection-container" style="margin-top: 20px;">
                <div class="feature-selection-card {"selected" if "Auto-Solver" in menu else ""}">
                    <span class="material-symbols-outlined card-icon">tune</span>
                    <h4>Auto-Solver</h4>
                    <p>Optimasi diameter pipa otomatis berbasis EPyT.</p>
                </div>
                <div class="feature-selection-card {"selected" if "Pressure" in menu else ""}">
                    <span class="material-symbols-outlined card-icon">valve</span>
                    <h4>Pressure & Auto-PRV</h4>
                    <p>Analisis tekanan node & Triple PRV.</p>
                </div>
                <div class="feature-selection-card {"selected" if "Hardy Cross" in menu else ""}">
                    <span class="material-symbols-outlined card-icon">account_tree</span>
                    <h4>Hardy Cross</h4>
                    <p>Analisis loop jaringan manual.</p>
                </div>
            </div>
        """)
        
        st.markdown("---")
        st.markdown("### Target Criteria")
        st.html("""
            <div class="feature-selection-container">
                <div class="feature-selection-card" style="padding: 16px;">
                    <span class="material-symbols-outlined card-icon" style="color:#007f64; margin-bottom:8px;">speed</span>
                    <h4 style="font-size:14px;">Pressure</h4>
                    <p style="font-size:12px;">10 - 80m</p>
                </div>
                <div class="feature-selection-card" style="padding: 16px;">
                    <span class="material-symbols-outlined card-icon" style="color:#007f64; margin-bottom:8px;">water_drop</span>
                    <h4 style="font-size:14px;">Velocity</h4>
                    <p style="font-size:12px;">0.3 - 2.5 m/s</p>
                </div>
                <div class="feature-selection-card" style="padding: 16px;">
                    <span class="material-symbols-outlined card-icon" style="color:#007f64; margin-bottom:8px;">timeline</span>
                    <h4 style="font-size:14px;">Headloss</h4>
                    <p style="font-size:12px;">Max 10 m/km</p>
                </div>
            </div>
        """)

    with col_right:
        st.html(f"""
            <div class="optimizer-workspace" style="margin-top: 0; grid-template-columns: 1fr;">
                <div class="log-card">
                    <div class="log-head">
                        <h3><span class="material-symbols-outlined" style="color:#0066cc;">terminal</span> Live Optimization Log</h3>
                        <span class="engine-pill">{selected_engine} Engine</span>
                    </div>
                    <div class="log-console">
                        10:42:01 Initializing EPANET workspace...<br>
                        10:42:02 Feature selected: {menu.split(" (")[0]}<br>
                        10:42:03 Waiting for .inp network upload...<br>
                        10:42:05 Evaluating Permen PU criteria...<br>
                        <span class="log-good">10:42:06 Ready to start optimization.</span>
                    </div>
                </div>
            </div>
            
            <div style="margin-top: 32px;">
                <div class="upload-title" style="text-align: left;">
                    <h2 class="hero-title" style="font-size: 32px;">Upload Your Network</h2>
                    <p class="hero-subtitle" style="margin: 0;">Drag and drop your .inp file here to begin.</p>
                </div>
                
                <div style="margin-top: 24px;">
                    uploaded_file = st.file_uploader("", type=["inp"])
                </div>
            </div>
        """)
        
        # We need to put the actual file uploader here outside the HTML block
        uploaded_file = st.file_uploader("", type=["inp"], key="main_uploader", label_visibility="collapsed")
        
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
            st.success("File validated. Ready to optimize.")
            if start_clicked:
                st.session_state['run_solver'] = True
                
        if st.session_state.get('run_solver', False):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".inp") as tmp:
                # pyrefly: ignore [missing-attribute]
                tmp.write(uploaded_file.getvalue())
                tmp_path = tmp.name

            try:
                with st.spinner(f"Optimizing Network... using {menu.split('(')[0].strip()}"):
                    if "Auto-Solver" in menu:
                        run_auto_solver(tmp_path)
                    elif "Pressure" in menu:
                        run_pressure_analysis(tmp_path)
                    elif "Hardy Cross" in menu:
                        run_hardy_cross(tmp_path)

            except Exception as e:
                st.error(f"Gagal menjalankan analisis: {str(e)}")
                st.exception(e)
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
            <div class="footer-links">
                <span>Regulatory Standards</span>
                <span>Technical Support</span>
            </div>
        </div>
    """)
