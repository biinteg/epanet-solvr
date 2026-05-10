# pyrefly: ignore [missing-import]
import streamlit as st
import tempfile
import os
import time
from datetime import datetime, timedelta, timezone
from views import styles
from modules.auto_solver import run_auto_solver
from modules.pressure_analysis import run_pressure_analysis
from modules.hardy_cross import run_hardy_cross
from modules.helpers import (
    warnai_status_solver, 
    warnai_status_tekanan, 
    tampilkan_network, 
    tampilkan_network_plotly,
    tampilkan_skema_jaringan
)

def add_log(msg, type='info'):
    if "log_history" not in st.session_state:
        st.session_state["log_history"] = []
    local_now = datetime.now(timezone.utc) + timedelta(hours=7)
    timestamp = local_now.strftime("%H:%M:%S")
    color = "#66d39b" if type == 'success' else "#ff4b4b" if type == 'error' else "#cfd6d4"
    if type == 'ultra': color = "#bb86fc" # Purple for ultra
    log_entry = f'<span style="color: {color};">{timestamp} {msg}</span>'
    st.session_state["log_history"].append(log_entry)
    if len(st.session_state["log_history"]) > 15:
        st.session_state["log_history"].pop(0)

def render():
    styles.inject_optimizer_styles()

    if "log_history" not in st.session_state:
        st.session_state["log_history"] = []
        add_log("Initializing EPANET workspace...")
        add_log("Ready for optimization.")

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
            <div class="dashboard-kicker">Multi-stage network optimization</div>
            <h1 class="dashboard-title">Optimization Dashboard</h1>
            <p class="dashboard-subtitle">
                Real-time analysis and automatic sizing of the water distribution network based on
                Permen PU No. 18/PRT/M/2007 criteria.
            </p>
        </div>
    """)

    col_left, col_right = st.columns([1, 2.8], gap="large")

    with col_left:
        st.markdown("### Select Strategy")
        feature_options = [
            "Auto-Solver Only", 
            "Pressure & Auto-PRV", 
            "Hardy Cross",
            "Ultra Optimize (All-in-One)",
            "Network Topology Visualizer"
        ]
        
        old_menu = st.session_state.get("last_selected_feature", "")
        menu = st.radio("Pilih fitur optimizer", feature_options, label_visibility="collapsed", key="feature_selector")
        
        if menu != old_menu:
            st.session_state["last_selected_feature"] = menu
            add_log(f"Strategy selected: {menu}")
            if "solver_results" in st.session_state: del st.session_state["solver_results"]
        
        selected_engine = "Multi-Core" if "Ultra" in menu else "EPyT" if "Auto" in menu else "WNTR"
        
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
                if "solver_results" in st.session_state: del st.session_state["solver_results"]

        # Settings for Ultra or Pressure
        target_prv = 50.0
        if "Pressure" in menu or "Ultra" in menu:
            st.markdown("---")
            st.markdown("### Pressure Control Settings")
            target_prv = st.number_input("Target Tekanan PRV (m)", value=50.0, min_value=10.0, max_value=100.0)

        col_btn1, col_btn2 = st.columns([2, 1])
        with col_btn1:
            btn_text = "ULTRA OPTIMIZE  ⚡" if "Ultra" in menu else "Start Analysis  →"
            start_clicked = st.button(btn_text, type="primary", use_container_width=True, disabled=uploaded_file is None)
        with col_btn2:
            if st.button("Clear Workspace", use_container_width=True):
                if "solver_results" in st.session_state: del st.session_state["solver_results"]
                st.session_state["log_history"] = []
                add_log("Workspace reset.")
                st.rerun()

        if start_clicked:
            add_log(f"Starting {menu} Process...", 'ultra' if "Ultra" in menu else 'info')
            with tempfile.NamedTemporaryFile(delete=False, suffix=".inp") as tmp:
                # pyrefly: ignore [missing-attribute]
                tmp.write(uploaded_file.getvalue())
                tmp_path = tmp.name

            try:
                results_container = {}
                with st.spinner(f"Processing..."):
                    if "Ultra" in menu:
                        # STAGE 1: Auto Solver
                        add_log("STAGE 1: Optimizing Pipe Diameters...", 'info')
                        res1 = run_auto_solver(tmp_path)
                        # STAGE 2: Pressure Analysis on optimized diameters
                        add_log("STAGE 2: Stabilizing Pressure & PRV Placement...", 'info')
                        res2 = run_pressure_analysis(res1["inp_file_path"], target_prv=target_prv, run_triple_prv=True)
                        
                        results_container = {
                            "type": "ultra",
                            "stage1": res1,
                            "stage2": res2,
                            "final_inp": (res2["prv_results"]["inp_path"] 
                                          if ("prv_results" in res2 and isinstance(res2["prv_results"], dict)) 
                                          else res1["inp_file_path"])
                        }
                        add_log("ULTRA OPTIMIZATION COMPLETE!", 'success')
                    elif "Auto-Solver" in menu:
                        results_container = run_auto_solver(tmp_path)
                    elif "Pressure" in menu:
                        results_container = run_pressure_analysis(tmp_path, target_prv=target_prv, run_triple_prv=True)
                    elif "Hardy Cross" in menu:
                        results_container = run_hardy_cross(tmp_path)
                    
                    st.session_state["solver_results"] = results_container
                st.rerun()

            except Exception as e:
                add_log(f"Critical Error: {str(e)}", 'error')
                st.error(f"Failed to process: {str(e)}")
            finally:
                if os.path.exists(tmp_path):
                    try: os.remove(tmp_path)
                    except: pass

        # Network Topology Visualizer (Feature ke-5)
        if uploaded_file and "Network Topology" in menu:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown("### 🗺️ Network Topology Visualization")
            with tempfile.NamedTemporaryFile(delete=False, suffix=".inp") as tmp:
                tmp.write(uploaded_file.getvalue())
                tmp_path = tmp.name
            try:
                # pyrefly: ignore [missing-import]
                import wntr
                wn_preview = wntr.network.WaterNetworkModel(tmp_path)
                tampilkan_skema_jaringan(wn_preview, judul=f"Skema: {uploaded_file.name}")
                add_log(f"Visualizing topology: {uploaded_file.name}", 'info')
            except Exception as e:
                st.error(f"Gagal memuat visualisasi: {e}")
            finally:
                if os.path.exists(tmp_path): os.remove(tmp_path)
            st.markdown('</div>', unsafe_allow_html=True)

        # Results Display
        if "solver_results" in st.session_state:
            res = st.session_state["solver_results"]
            st.markdown("---")
            
            if res["type"] == "ultra":
                st.success("⚡ Ultra Optimization Finished. Combined Auto-Diameter and Triple PRV Stabilization.")
                tabs = st.tabs(["Diameters (Stage 1)", "Pressure (Stage 2)", "Final Network"])
                with tabs[0]:
                    st.markdown("### Hasil Optimasi Diameter")
                    df1 = res["stage1"]["df"]
                    if "Status" in df1.columns:
                        st.dataframe(df1.style.map(warnai_status_solver, subset=["Status"]), use_container_width=True)
                    else:
                        st.dataframe(df1, use_container_width=True)
                with tabs[1]:
                    st.markdown("### Perbandingan Tekanan Final")
                    if "prv_results" in res["stage2"]:
                        st.success(f"PRV installed on: {', '.join(res['stage2']['prv_results']['best_combo'])}")
                        df2 = res["stage2"]["prv_results"]["df_compare"]
                        if "Status" in df2.columns:
                            st.dataframe(df2.style.map(warnai_status_tekanan, subset=["Status"]), use_container_width=True)
                        else:
                            st.dataframe(df2, use_container_width=True)
                    else:
                        df2_awal = res["stage2"]["df_awal"]
                        if "Status" in df2_awal.columns:
                            st.dataframe(df2_awal.style.map(warnai_status_tekanan, subset=["Status"]), use_container_width=True)
                        else:
                            st.dataframe(df2_awal, use_container_width=True)
                with tabs[2]:
                    st.markdown("### Visualisasi Akhir")
                    viz_mode = st.radio("Mode Visualisasi", ["Static Map", "Interactive (Plotly)"], horizontal=True, key="ultra_viz")
                    final_network = res["stage2"]["prv_results"]["best_network"] if "prv_results" in res["stage2"] else res["stage2"]["wn_initial"]
                    final_pressures = res["stage2"]["prv_results"]["best_result"] if "prv_results" in res["stage2"] else res["stage2"]["tekanan_awal"]
                    
                    if viz_mode == "Static Map":
                        tampilkan_network(final_network, final_pressures, "Network Topology After Ultra Optimization")
                    else:
                        tampilkan_network_plotly(final_network, final_pressures, "Interactive Topology (Hover to see Pressure)")
                    
                with open(res["final_inp"], "rb") as f:
                    st.download_button("📥 DOWNLOAD ULTRA OPTIMIZED NETWORK (.inp)", data=f, file_name="Ultra_Optimized_Result.inp", mime="text/plain", use_container_width=True)

            elif res["type"] == "pressure":
                st.markdown("### 📊 Diagnosis Tekanan")
                if "prv_results" in res:
                    st.success(f"✅ Triple PRV Optimization Complete. Best combo: {', '.join(res['prv_results']['best_combo'])}")
                    
                    tabs_p = st.tabs(["📊 Pressure Comparison", "🗺️ Final Map"])
                    with tabs_p[0]:
                        df_comp = res["prv_results"]["df_compare"]
                        st.dataframe(df_comp.style.map(warnai_status_tekanan, subset=["Status"]), use_container_width=True)
                        
                        # Download button
                        with open(res["prv_results"]["inp_path"], "rb") as f:
                            st.download_button("📥 Download Optimized Network (.inp)", data=f, file_name="PRV_Optimized_Result.inp", use_container_width=True)
                    
                    with tabs_p[1]:
                        viz_mode_p = st.radio("Mode Visualisasi", ["Static Map", "Interactive (Plotly)"], horizontal=True, key="press_viz")
                        if viz_mode_p == "Static Map":
                            tampilkan_network(res["prv_results"]["best_network"], res["prv_results"]["best_result"], "Final Network with Triple PRV")
                        else:
                            tampilkan_network_plotly(res["prv_results"]["best_network"], res["prv_results"]["best_result"], "Interactive Pressure Map")
                else:
                    st.warning("⚠️ No Triple PRV combination found that improves the network or matches the safety criteria.")
                    st.dataframe(res["df_awal"].style.map(warnai_status_tekanan, subset=["Status"]), use_container_width=True)

            elif res["type"] == "auto_solver":
                st.markdown("### 📊 Ringkasan Optimasi Diameter")
                st.info("💡 Tip: Gunakan fitur 'Ultra Optimize' untuk menggabungkan optimasi ini dengan stabilisasi tekanan otomatis.")
                df_auto = res["df"]
                if "Status" in df_auto.columns:
                    st.dataframe(df_auto.style.map(warnai_status_solver, subset=["Status"]), use_container_width=True)
                else:
                    st.dataframe(df_auto, use_container_width=True)
                with open(res["inp_file_path"], "rb") as f:
                    st.download_button("📥 Download Optimized Network", data=f, file_name="Diameter_Optimized.inp", use_container_width=True)

            elif res["type"] == "hardy_cross":
                st.success(f"⚖️ Hardy Cross Analysis Finished in {res['iterations']} iterations.")
                h_tabs = st.tabs(["Iterasi Loop", "Debit Final", "Final Network"])
                with h_tabs[0]:
                    st.markdown("### Log Konvergensi Loop")
                    st.dataframe(res["history_df"], use_container_width=True)
                with h_tabs[1]:
                    st.markdown("### Perbandingan Debit Awal vs Akhir")
                    st.dataframe(res["final_df"], use_container_width=True)
                with h_tabs[2]:
                    st.markdown("### Visualisasi Aliran")
                    dummy_tekanan = {n: 0 for n in res["wn"].node_name_list}
                    tampilkan_network(res["wn"], dummy_tekanan, "Hardy Cross Flow Distribution")

    st.html("""
        <div class="footer">
            <div class="footer-brand">EPANET Solver</div>
            <div class="footer-copy">© 2026 EPANET Solver. Compliance: Permen PU Standards.</div>
        </div>
    """)
