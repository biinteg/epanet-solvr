import streamlit as st
from views import styles

def render():
    styles.inject_landing_styles()

    st.html("""
        <div class="top-nav">
            <div class="nav-brand">EPANET Solver</div>
            <div class="nav-links">
                <a class="nav-link active" href="?page=home" target="_self">Home</a>
                <a class="nav-link" href="?page=optimizer" target="_self">Optimizer</a>
                <a class="nav-link" href="#documentation" target="_self">Documentation</a>
            </div>
            <div class="nav-actions" aria-label="Account notifications">
                <span class="material-symbols-outlined">account_circle</span>
                <span class="material-symbols-outlined">notifications</span>
            </div>
        </div>

        <div class="hero-wrapper">
            <div style="display: flex; gap: 48px; align-items: center; flex-wrap: wrap;">
                <div style="flex: 1; min-width: 300px;">
                    <h1 class="hero-title">Optimize Your Water Network with Precision</h1>
                    <p class="hero-subtitle">Automatically iterate pipe diameters to meet Permen PU No. 18/PRT/M/2007 standards. Save time and ensure compliance effortlessly.</p>
                </div>
                <div style="flex: 1; min-width: 300px;">
                    <div class="hero-image-container">
                        <img class="hero-image" src="https://lh3.googleusercontent.com/aida-public/AB6AXuB4959cl0eiufQMoP3c7ofSocNSRKd6nCUpaOkjH_9PNor_RgbKku2RdYN34FmCO0vvTuQ_AWqywSuOrx8ZNKmc5mlrmnXzg3W3CEFnm4Gt9AQefNnAEtYwFz2zh-ulW3MX_C2dzpfjE3nEVSnzoNKlG0oSm9RNPuTWxUaP_OJ_nIQ_S-4G1YeWZwbPlYbw-zdpv8GupmDIpj2vYlQsyhZ6h_okZurYcTwNIUQDWNPVINLDJYsiKgUw_yo7nJUQZJDxZU-EmajKXw4" alt="Water Network Visualization">
                    </div>
                </div>
            </div>
        </div>
    """)
    
    col1, col2 = st.columns([1, 1])
    with col1:
        c1, c2, c3 = st.columns([1, 1, 1])
        with c1:
            if st.button("Get Started", type="primary", key="hero_start", use_container_width=True):
                st.session_state["app_started"] = True
                st.query_params["page"] = "optimizer"
                st.rerun()
        with c2:
            st.button("View Documentation", key="hero_docs", use_container_width=True)

    st.html("""
        <div class="problem-section">
            <h2 class="problem-headline">Still struggling with manual water network analysis?</h2>
            <p class="problem-subheadline">
                Manual iteration of pipe diameters is time-consuming, prone to human error, and often results in networks that fail to meet strict hydraulic compliance standards.
            </p>
            <div class="pain-points-grid">
                <div class="pain-point-card">
                    <div class="pain-point-icon"><span class="material-symbols-outlined" style="font-variation-settings: 'FILL' 1;">schedule</span></div>
                    <h3 class="pain-point-title">Wasted Time</h3>
                    <p class="pain-point-desc">Hours spent manually updating pipe sizes and re-running simulations for every minor network change.</p>
                </div>
                <div class="pain-point-card">
                    <div class="pain-point-icon"><span class="material-symbols-outlined" style="font-variation-settings: 'FILL' 1;">warning</span></div>
                    <h3 class="pain-point-title">Compliance Risks</h3>
                    <p class="pain-point-desc">Difficulty ensuring all nodes and links meet the strict pressure and velocity standards of Permen PU No. 18/PRT/M/2007.</p>
                </div>
                <div class="pain-point-card">
                    <div class="pain-point-icon"><span class="material-symbols-outlined" style="font-variation-settings: 'FILL' 1;">analytics</span></div>
                    <h3 class="pain-point-title">Suboptimal Design</h3>
                    <p class="pain-point-desc">Trial-and-error approaches often lead to oversized pipes, unnecessarily increasing project construction costs.</p>
                </div>
            </div>
        </div>
    """)

    st.html("""
        <div class="bento-grid">
            <div class="bento-card">
                <div class="bento-icon icon-1"><span class="material-symbols-outlined">autorenew</span></div>
                <h3 class="bento-title">Auto-Iterate</h3>
                <p class="bento-text">Melakukan iterasi penggantian diameter pipa secara otomatis. Menggunakan daftar ukuran standar pipa komersial: 40 mm hingga 315 mm.</p>
            </div>
            <div class="bento-card">
                <div class="bento-icon icon-2"><span class="material-symbols-outlined">verified_user</span></div>
                <h3 class="bento-title">Hydraulic Compliance</h3>
                <p class="bento-text">Mengevaluasi kondisi hidrolis ketat berdasarkan Permen PU No. 18/PRT/M/2007 untuk tekanan, kecepatan, dan headloss.</p>
            </div>
            <div class="bento-card">
                <div class="bento-icon icon-3"><span class="material-symbols-outlined">download</span></div>
                <h3 class="bento-title">Instant .inp Export</h3>
                <p class="bento-text">Setelah selesai, unduh file .inp baru yang diameternya telah dioptimasi, siap digunakan kembali di EPANET Desktop.</p>
            </div>
        </div>
        
        <div class="footer">
            © 2026 EPANET Solver. Compliance: Permen PU Standards.
        </div>
    """)
