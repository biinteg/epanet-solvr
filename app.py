import streamlit as st
import tempfile
import os

from modules.auto_solver import run_auto_solver
from modules.pressure_analysis import run_pressure_analysis
from modules.hardy_cross import run_hardy_cross

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="EPANET Solver",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Global CSS adapted from design.md
st.html("""
    <link href="https://fonts.googleapis.com/css2?family=Hanken+Grotesk:wght@400;500;600;700;800;900&display=swap" rel="stylesheet"/>
    <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap" rel="stylesheet"/>
    <style>
    :root {
        --primary: #004e9f;
        --surface: #f9f9fb;
        --on-surface: #1a1c1d;
        --on-surface-variant: #414753;
        --surface-container-low: #f3f3f5;
        --surface-container-lowest: #ffffff;
        --outline-variant: #c1c6d5;
        --secondary-container: #6cf8bb;
        --on-secondary-container: #00714d;
        --primary-fixed: #d7e3ff;
        --tertiary-fixed: #ffdbcb;
        --on-tertiary-fixed: #341100;
    }
    
    html, body, [class*="css"] {
        font-family: 'Hanken Grotesk', sans-serif !important;
    }

    /* Force dark text on primary buttons for better contrast */
    .stButton > button[kind="primary"] {
        background-color: var(--primary) !important;
        color: #ffffff !important;
        border-radius: 9999px !important;
        font-weight: 600 !important;
        padding: 10px 24px !important;
        border: none !important;
        box-shadow: 0px 4px 14px rgba(0,0,0,0.1) !important;
    }
    
    .stButton > button[kind="secondary"] {
        border-radius: 9999px !important;
        font-weight: 600 !important;
        padding: 10px 24px !important;
        border: 1px solid var(--outline-variant) !important;
        background-color: var(--surface) !important;
        color: var(--on-surface) !important;
    }

    /* Inputs Styling */
    .stTextInput > div > div > input, 
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > div {
        background-color: #F5F5F7 !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 12px 16px !important;
        color: var(--on-surface) !important;
        transition: border 0.2s ease !important;
    }
    
    .stTextInput > div > div > input:focus, 
    .stNumberInput > div > div > input:focus,
    .stSelectbox > div > div > div:focus-within {
        border: 1px solid var(--primary) !important;
        outline: none !important;
    }

    /* File Uploader Card */
    [data-testid="stFileUploadDropzone"] {
        background-color: #ffffff !important;
        border: 2px dashed #c1c6d5 !important;
        border-radius: 10px !important;
        min-height: 315px !important;
        padding: 48px 32px !important;
        box-shadow: 0px 18px 50px rgba(21, 37, 65, 0.06) !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }
    [data-testid="stFileUploader"] {
        max-width: 820px;
        margin: 0 auto;
    }
    [data-testid="stFileUploader"] label {
        display: none !important;
    }
    [data-testid="stFileUploadDropzone"] svg {
        color: #b7becd !important;
        width: 54px !important;
        height: 54px !important;
    }
    [data-testid="stFileUploadDropzone"] button {
        background-color: #eceef2 !important;
        color: #0b1220 !important;
        border: 0 !important;
        border-radius: 8px !important;
        padding: 10px 24px !important;
        font-weight: 600 !important;
    }
    [data-testid="stFileUploadDropzone"] div {
        color: #0b1220 !important;
    }

    /* Hero Section Styling */
    .hero-wrapper {
        padding: 60px 0;
        text-align: left;
    }
    .hero-title {
        font-size: 48px;
        font-weight: 700;
        line-height: 1.1;
        letter-spacing: -0.02em;
        margin-bottom: 24px;
        color: var(--on-surface);
    }
    .hero-subtitle {
        font-size: 17px;
        font-weight: 400;
        line-height: 1.5;
        color: var(--on-surface-variant);
        max-width: 600px;
        margin-bottom: 32px;
    }
    .hero-image-container {
        width: 100%;
        height: 400px;
        border-radius: 24px;
        overflow: hidden;
        position: relative;
        box-shadow: 0px 10px 40px rgba(0,0,0,0.04);
        background: linear-gradient(135deg, var(--primary-fixed), var(--secondary-container));
    }
    .hero-image {
        width: 100%;
        height: 100%;
        object-fit: cover;
        opacity: 0.9;
    }

    /* Features Bento Grid */
    .bento-grid {
        display: flex;
        gap: 24px;
        justify-content: center;
        margin-top: 60px;
        flex-wrap: wrap;
    }
    .bento-card {
        background-color: var(--surface-container-low);
        border-radius: 12px;
        padding: 32px;
        width: 320px;
        box-shadow: 0px 10px 40px rgba(0,0,0,0.04);
        text-align: left;
        transition: transform 0.3s ease;
    }
    .bento-card:hover {
        transform: translateY(-4px);
    }
    .bento-icon {
        width: 48px;
        height: 48px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 16px;
    }
    .icon-1 { background-color: var(--primary-fixed); color: var(--primary); }
    .icon-2 { background-color: var(--secondary-container); color: var(--on-secondary-container); }
    .icon-3 { background-color: var(--tertiary-fixed); color: var(--on-tertiary-fixed); }

    .bento-title {
        font-size: 24px;
        font-weight: 600;
        margin-bottom: 8px;
        color: var(--on-surface);
        line-height: 1.3;
    }
    .bento-text {
        font-size: 15px;
        color: var(--on-surface-variant);
        line-height: 1.5;
    }

    /* Problem Section */
    .problem-section {
        padding: 64px 20px;
        background-color: var(--surface-container-lowest);
        text-align: center;
        margin-top: 40px;
    }
    .problem-headline {
        font-size: 32px;
        font-weight: 700;
        color: var(--on-surface);
        margin-bottom: 16px;
        letter-spacing: -0.01em;
    }
    .problem-subheadline {
        font-size: 17px;
        color: var(--on-surface-variant);
        max-width: 700px;
        margin: 0 auto 48px auto;
        line-height: 1.5;
    }
    .pain-points-grid {
        display: flex;
        gap: 24px;
        justify-content: center;
        flex-wrap: wrap;
        max-width: 1200px;
        margin: 0 auto;
    }
    .pain-point-card {
        background-color: var(--surface-container-low);
        border-radius: 12px;
        padding: 32px;
        width: 320px;
        text-align: left;
    }
    .pain-point-icon {
        color: var(--primary);
        font-size: 32px;
        margin-bottom: 16px;
    }
    .pain-point-title {
        font-size: 20px;
        font-weight: 600;
        color: var(--on-surface);
        margin-bottom: 8px;
    }
    .pain-point-desc {
        font-size: 15px;
        color: var(--on-surface-variant);
        line-height: 1.5;
    }

    /* Top Nav Bar replacement */
    .top-nav {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 18px 28px;
        background-color: #ffffff;
        box-shadow: none;
        margin: 0 -10px 18px -10px;
        border-radius: 0;
    }
    .nav-brand {
        font-size: 24px;
        font-weight: 700;
        color: var(--on-surface);
    }
    .nav-links {
        display: flex;
        gap: 32px;
        font-size: 14px;
        font-weight: 700;
    }
    .nav-link {
        color: var(--on-surface-variant);
        text-decoration: none;
        cursor: pointer;
    }
    .nav-link.active {
        color: var(--primary);
        font-weight: 700;
        border-bottom: 3px solid var(--primary);
        padding-bottom: 8px;
    }
    .nav-actions {
        display: flex;
        align-items: center;
        gap: 18px;
        color: #5b6270;
    }
    .nav-actions .material-symbols-outlined {
        font-size: 25px;
    }
    
    /* Footer */
    .footer {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 24px;
        padding: 32px 52px;
        margin: 80px -10px 0 -10px;
        background-color: #f4f5f7;
        border-top: 0;
        color: var(--on-surface-variant);
        font-size: 13px;
    }
    .footer-brand {
        color: #0b1220;
        font-weight: 800;
    }
    .footer-copy {
        color: #007f64;
    }
    .footer-links {
        display: flex;
        gap: 26px;
        color: #17213a;
        font-size: 13px;
        white-space: nowrap;
    }

    /* Metric cards for Upload Page */
    .metric-grid {
        display: flex;
        justify-content: center;
        gap: 16px;
        margin: 32px auto 40px auto;
        flex-wrap: wrap;
        max-width: 820px;
    }
    .metric-card {
        background-color: #f4f5f7;
        border-radius: 8px;
        padding: 20px 24px 18px 24px;
        text-align: center;
        min-width: 236px;
    }
    .metric-title {
        font-size: 13px;
        font-weight: 700;
        color: var(--on-surface);
        margin: 8px 0 4px 0;
    }
    .metric-val {
        font-size: 15px;
        color: var(--on-surface-variant);
    }
    .upload-title {
        padding-top: 12px;
        padding-bottom: 20px;
        text-align: center;
    }
    .upload-title .hero-title {
        font-size: 46px;
        margin: 0 auto 10px auto;
    }
    .upload-title .hero-subtitle {
        margin: 0 auto;
        color: #17213a;
    }
    .optimizer-action {
        max-width: 300px;
        margin: 0 auto;
    }
    .optimizer-action .stButton > button {
        min-height: 62px;
        font-size: 22px !important;
        border-radius: 9999px !important;
        box-shadow: 0px 10px 24px rgba(0, 78, 159, 0.28) !important;
    }
    @media (max-width: 760px) {
        .top-nav, .footer {
            flex-direction: column;
            align-items: flex-start;
        }
        .footer-links {
            flex-wrap: wrap;
            gap: 14px;
        }
        .metric-card {
            width: 100%;
        }
        .upload-title .hero-title {
            font-size: 34px;
        }
    }
    </style>
""")

if "app_started" not in st.session_state:
    st.session_state["app_started"] = False

page_param = st.query_params.get("page", "")
if page_param == "optimizer":
    st.session_state["app_started"] = True
elif page_param == "home":
    st.session_state["app_started"] = False

if not st.session_state["app_started"]:
    # =====================================================
    # LANDING PAGE
    # =====================================================
    st.html("""
        <style>
        /* Hide sidebar and header on landing page */
        [data-testid="collapsedControl"] {display: none;}
        header {display: none !important;}
        section[data-testid="stSidebar"] {display: none !important;}
        </style>

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
                    <div style="display: flex; gap: 16px;">
                        <div id="btn-started"></div>
                        <div id="btn-docs"></div>
                    </div>
                </div>
                <div style="flex: 1; min-width: 300px;">
                    <div class="hero-image-container">
                        <img class="hero-image" src="https://lh3.googleusercontent.com/aida-public/AB6AXuB4959cl0eiufQMoP3c7ofSocNSRKd6nCUpaOkjH_9PNor_RgbKku2RdYN34FmCO0vvTuQ_AWqywSuOrx8ZNKmc5mlrmnXzg3W3CEFnm4Gt9AQefNnAEtYwFz2zh-ulW3MX_C2dzpfjE3nEVSnzoNKlG0oSm9RNPuTWxUaP_OJ_nIQ_S-4G1YeWZwbPlYbw-zdpv8GupmDIpj2vYlQsyhZ6h_okZurYcTwNIUQDWNPVINLDJYsiKgUw_yo7nJUQZJDxZU-EmajKXw4" alt="Water Network Visualization">
                    </div>
                </div>
            </div>
        </div>
    """)
    
    # Injected buttons into the placeholders above using columns for interactivity
    # Note: Using absolute positioning hack or just columns if needed, but for hero it's better to use native columns
    # Let's use standard columns for the buttons instead of IDs
    
    col1, col2 = st.columns([1, 1])
    with col1:
        c1, c2, c3 = st.columns([1, 1, 1])
        with c1:
            if st.button("Get Started", type="primary", use_container_width=True):
                st.session_state["app_started"] = True
                st.rerun()
        with c2:
            st.button("View Documentation", use_container_width=True)

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

else:
    # =====================================================
    # MAIN APP (UPLOADER & SOLVERS)
    # =====================================================
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

    # Move sidebar navigation here
    st.sidebar.title("EPANET Solver Settings")
    
    menu = st.sidebar.radio(
        "Navigasi Modul:",
        [
            "Auto-Solver (Engine: EPyT)",
            "Analisis Tekanan & Auto-PRV (Engine: WNTR)",
            "Analisis Loop (Metode Hardy Cross)"
        ]
    )

    st.sidebar.markdown("---")
    
    if st.sidebar.button("← Kembali ke Beranda"):
        st.session_state["app_started"] = False
        st.session_state["run_solver"] = False
        st.query_params["page"] = "home"
        st.rerun()

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
            st.session_state['run_solver'] = False

    # =====================================================
    # MAIN
    # =====================================================

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
                    # =================================================
                    # FEATURE 1 : AUTO SOLVER
                    # =================================================
                    if menu == "Auto-Solver (Engine: EPyT)":
                        run_auto_solver(tmp_path)

                    # =================================================
                    # FEATURE 2 : ANALISIS TEKANAN + PRV
                    # =================================================
                    elif menu == "Analisis Tekanan & Auto-PRV (Engine: WNTR)":
                        run_pressure_analysis(tmp_path)

                    # =================================================
                    # FEATURE 3 : HARDY CROSS
                    # =================================================
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
