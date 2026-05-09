# pyrefly: ignore [missing-import]
import streamlit as st
import tempfile
import os
import time
from datetime import datetime, timedelta
from views import styles
from modules.auto_solver import run_auto_solver
from modules.pressure_analysis import run_pressure_analysis
from modules.hardy_cross import run_hardy_cross
from modules.helpers import warnai_status_solver, warnai_status_tekanan, tampilkan_network

def add_log(msg, type='info'):
    if "log_history" not in st.session_state:
        st.session_state["log_history"] = []
    local_now = datetime.utcnow() + timedelta(hours=7)
    timestamp = local_now.strftime("%H:%M:%S")
    color = "#66d39b" if type == 'success' else "#ff4b4b" if type == 'error' else "#cfd6d4"
    log_entry = f'<span style="color: {color};">{timestamp} {msg}</span>'
    st.session_state["log_history"].append(log_entry)
    if len(st.session_state["log_history"]) > 15:
        st.session_state["log_history"].pop(0)

def render():
    styles.inject_optimizer_styles()

    if "log_history" not in st.session_state:
        st.session_state["log_history"] = []
        add_log("Initializing EPANET workspace...")
        add_log("Ready for network upload.")

    st.html("""
        <div class="top-nav">
            <div class="nav-brand">EPANET Solver</div>
            <div class="nav-links">
                <a class="nav-link" href="?page=home" target="_self">Home</a>
                <a class="nav-link active" href="?page=optimizer" target="_self">Optimizer</a>
                <a class="nav-link" href="#documentation" target="_self">Documentation</a>
            </div>
            <div class="nav-actions">
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

    col_left, col_right = st.columns([1, 2.8], gap="large")

    with col_left:
        st.markdown("### Select Feature")
        feature_options = ["Auto-Solver", "Pressure & Auto-PRV", "Hardy Cross"]
        
        old_menu = st.session_state.get("last_selected_feature", "")
        menu = st.radio("Pilih fitur optimizer", feature_options, label_visibility="collapsed", key="feature_selector")
        
        if menu != old_menu:
            st.session_state["last_selected_feature"] = menu
            add_log(f"Feature selected: {menu}")
            if "solver_results" in st.session_state:
                del st.session_state["solver_results"]
        
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
                st.session_state.file_logged = uploaded_file.name
                if "solver_results" in st.session_state:
                    del st.session_state["solver_results"]

        # Feature-specific parameters
        target_prv = 50.0
        if "Pressure" in menu:
            st.markdown("---")
            st.markdown("### Pressure Analysis Settings")
            target_prv = st.number_input("Target Tekanan PRV (m)", value=50.0, min_value=10.0, max_value=100.0)
            run_triple = st.checkbox("Cari Kombinasi Triple PRV (Bisa memakan waktu lama)", value=False)
        else:
            run_triple = False

        col_btn1, col_btn2 = st.columns([2, 1])
        with col_btn1:
            start_clicked = st.button("Start Analysis  →", type="primary", use_container_width=True, disabled=uploaded_file is None)
        with col_btn2:
            if st.button("Clear Dashboard", use_container_width=True):
                if "solver_results" in st.session_state: del st.session_state["solver_results"]
                st.session_state["log_history"] = []
                add_log("Workspace reset.")
                st.rerun()

        if start_clicked:
            add_log(f"Initiating {menu} Engine...", 'info')
            with tempfile.NamedTemporaryFile(delete=False, suffix=".inp") as tmp:
                # pyrefly: ignore [missing-attribute]
                tmp.write(uploaded_file.getvalue())
                tmp_path = tmp.name

            try:
                add_log("Preprocessing network data...")
                with st.spinner(f"Running {menu}..."):
                    if "Auto-Solver" in menu:
                        results = run_auto_solver(tmp_path)
                    elif "Pressure" in menu:
                        results = run_pressure_analysis(tmp_path, target_prv=target_prv, run_triple_prv=run_triple)
                    elif "Hardy Cross" in menu:
                        results = run_hardy_cross(tmp_path)
                    
                    st.session_state["solver_results"] = results
                    add_log("Analysis successfully completed.", 'success')
                st.rerun()

            except Exception as e:
                add_log(f"Critical Error: {str(e)}", 'error')
                st.error(f"Failed to process: {str(e)}")
            finally:
                if os.path.exists(tmp_path):
                    try: os.remove(tmp_path)
                    except: pass

        # Results Display
        if "solver_results" in st.session_state:
            res = st.session_state["solver_results"]
            st.markdown("---")
            
            if res["type"] == "pressure":
                st.markdown("### 📊 Diagnosis Tekanan Awal")
                m1, m2, m3 = st.columns(3)
                m1.metric("Terlalu Rendah", res["metrics_awal"]["low"])
                m2.metric("Terlalu Tinggi", res["metrics_awal"]["high"])
                m3.metric("Total Junction", res["metrics_awal"]["total"])
                st.dataframe(res["df_awal"].style.map(warnai_status_tekanan, subset=["Status"]), use_container_width=True, height=300)
                tampilkan_network(res["wn_initial"], res["tekanan_awal"], "Visualisasi Tekanan Awal")
                
                if "prv_results" in res:
                    st.markdown("### 🛠️ Hasil Optimasi Triple PRV")
                    st.success(f"Kombinasi Terbaik: **{', '.join(res['prv_results']['best_combo'])}**")
                    st.metric("Node Aman", f"{res['prv_results']['best_score']}/{res['metrics_awal']['total']}")
                    st.dataframe(res["prv_results"]["df_compare"].style.map(warnai_status_tekanan, subset=["Status"]), use_container_width=True, height=300)
                    tampilkan_network(res["prv_results"]["best_network"], res["prv_results"]["best_result"], "Visualisasi Setelah Triple PRV")
                    with open(res["prv_results"]["inp_path"], "rb") as f:
                        st.download_button("📥 Download Triple PRV Network (.inp)", data=f, file_name="Triple_PRV_Result.inp", mime="text/plain", use_container_width=True)

            elif res["type"] == "hardy_cross":
                st.markdown("### 📊 Hasil Hardy Cross")
                st.info(f"Loop ditemukan: {res['loops_found']} | Iterasi: {res['iterations']} | Status: {'Konvergen' if res['converged'] else 'Tidak Konvergen'}")
                c1, c2 = st.columns(2)
                with c1: st.markdown("**Sejarah Koreksi ΔQ**"); st.dataframe(res["history_df"], height=300)
                with c2: st.markdown("**Debit Final (L/s)**"); st.dataframe(res["final_df"], height=300)
                # Note: Visualization for Hardy Cross uses Matplotlib, which might need special handling if it fails
                st.info("Visualisasi aliran tersedia di backend (matplotlib).")

            elif res["type"] == "auto_solver":
                st.markdown("### 📊 Ringkasan Optimasi Diameter")
                m1, m2, m3 = st.columns(3)
                m1.metric("Total Pipa", res["metrics"]["total"])
                m2.metric("Dimodifikasi", res["metrics"]["changed"])
                m3.metric("Kepatuhan PU", f"{res['metrics']['compliant']}/{res['metrics']['total']}")
                st.dataframe(res["df"].style.map(warnai_status_solver, subset=["Status Optimasi"]), use_container_width=True, height=300)
                with open(res["inp_file_path"], "rb") as f:
                    st.download_button("📥 Download Optimized Network (.inp)", data=f, file_name="Optimized_Network.inp", mime="text/plain", use_container_width=True)

    st.html("""
        <div class="footer">
            <div class="footer-brand">EPANET Solver</div>
            <div class="footer-copy">© 2026 EPANET Solver. Compliance: Permen PU Standards.</div>
        </div>
    """)
