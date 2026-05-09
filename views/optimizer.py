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
            <div class="dashboard-grid">
                <div class="status-card">
                    <div class="status-label"><span class="material-symbols-outlined" style="color:#dc2626;">warning</span>Violations</div>
                    <div class="status-value">0</div>
                    <div class="status-caption">Detected after analysis</div>
                </div>
                <div class="status-card">
                    <div class="status-label"><span class="material-symbols-outlined" style="color:#0066cc;">autorenew</span>Iterations</div>
                    <div class="status-value">Ready</div>
                    <div class="status-caption">Select feature and upload file</div>
                </div>
                <div class="status-card">
                    <div class="status-label"><span class="material-symbols-outlined" style="color:#007f64;">speed</span>Target Criteria</div>
                    <div class="status-value">10-80m</div>
                    <div class="status-caption">Pressure, velocity, headloss</div>
                </div>
            </div>
            <div class="feature-grid">
                <div class="feature-card">
                    <span class="material-symbols-outlined feature-icon">tune</span>
                    <h3>Auto-Solver</h3>
                    <p>Optimasi diameter pipa otomatis berbasis EPyT untuk memenuhi velocity dan headloss.</p>
                </div>
                <div class="feature-card">
                    <span class="material-symbols-outlined feature-icon">valve</span>
                    <h3>Pressure & Auto-PRV</h3>
                    <p>Analisis tekanan node dan pencarian kombinasi Triple PRV terbaik berbasis WNTR.</p>
                </div>
                <div class="feature-card">
                    <span class="material-symbols-outlined feature-icon">account_tree</span>
                    <h3>Hardy Cross</h3>
                    <p>Analisis loop jaringan menggunakan metode Hardy Cross untuk pemeriksaan debit.</p>
                </div>
            </div>
        </div>
    """)

    feature_options = [
        "Auto-Solver (Engine: EPyT)",
        "Analisis Tekanan & Auto-PRV (Engine: WNTR)",
        "Analisis Loop (Metode Hardy Cross)"
    ]
    menu = st.radio(
        "Pilih fitur optimizer",
        feature_options,
        horizontal=True,
        label_visibility="collapsed"
    )

    selected_engine = "EPyT" if "EPyT" in menu else "WNTR" if "WNTR" in menu else "Manual Loop"
    st.html(f"""
        <div class="dashboard-shell">
            <div class="optimizer-workspace">
                <div class="summary-card">
                    <h3>Network Summary</h3>
                    <div class="summary-row"><span>Selected Feature</span><strong>{menu.split(" (")[0]}</strong></div>
                    <div class="summary-row"><span>Engine</span><strong>{selected_engine}</strong></div>
                    <div class="summary-row"><span>Pressure</span><strong>10 - 80 m</strong></div>
                    <div class="summary-row"><span>Velocity</span><strong>0.3 - 2.5 m/s</strong></div>
                    <div class="summary-row"><span>Headloss</span><strong>&le; 10 m/km</strong></div>
                </div>
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
        </div>
    """)

    st.html("""
        <div class="upload-title">
            <h1 class="hero-title">Upload Your Network</h1>
            <p class="hero-subtitle">Drag and drop your .inp file here to begin the optimization process.</p>
        </div>
    """)

    # Container for uploader
    col1, col2, col3 = st.columns([1, 4, 1])
    with col2:
        uploaded_file = st.file_uploader("", type=["inp"])

        st.html("""
            <div class="metric-grid">
                <div class="metric-card">
                    <span class="material-symbols-outlined" style="color: #007f64; font-size: 32px; font-variation-settings: 'FILL' 1;">speed</span>
                    <h3 class="metric-title">Pressure</h3>
                    <p class="metric-val">10 - 80m</p>
                </div>
                <div class="metric-card">
                    <span class="material-symbols-outlined" style="color: #007f64; font-size: 32px; font-variation-settings: 'FILL' 1;">water_drop</span>
                    <h3 class="metric-title">Velocity</h3>
                    <p class="metric-val">0.3 - 2.5 m/s</p>
                </div>
                <div class="metric-card">
                    <span class="material-symbols-outlined" style="color: #007f64; font-size: 32px; font-variation-settings: 'FILL' 1;">timeline</span>
                    <h3 class="metric-title">Headloss</h3>
                    <p class="metric-val">Max 10 m/km</p>
                </div>
            </div>
        """)
        
        if uploaded_file is None:
            st.info("Pilih fitur optimizer di atas, lalu unggah file .inp untuk memulai.")
            st.session_state['run_solver'] = False

        action_left, action_mid, action_right = st.columns([1.15, 1, 1.15])
        with action_mid:
            start_clicked = st.button(
                "Start Optimization  →",
                type="primary",
                use_container_width=True,
                disabled=uploaded_file is None,
            )

        if uploaded_file is not None:
            st.success("File validated. Ready to optimize.")
            if start_clicked:
                st.session_state['run_solver'] = True
                
        if st.session_state.get('run_solver', False):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".inp") as tmp:
                tmp.write(uploaded_file.getvalue())
                tmp_path = tmp.name

            try:
                # Add a visually engaging loading/processing message (mimicking design)
                with st.spinner(f"Optimizing Network... using {menu.split('(')[0].strip()}"):
                    if menu == "Auto-Solver (Engine: EPyT)":
                        run_auto_solver(tmp_path)
                    elif menu == "Analisis Tekanan & Auto-PRV (Engine: WNTR)":
                        run_pressure_analysis(tmp_path)
                    elif menu == "Analisis Loop (Metode Hardy Cross)":
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
                <span>Terms of Service</span>
                <span>Privacy Policy</span>
            </div>
        </div>
    """)
