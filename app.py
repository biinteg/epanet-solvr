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
    page_title="EPANET Pro Toolkit",
    layout="wide",
    initial_sidebar_state="collapsed"
)

if "app_started" not in st.session_state:
    st.session_state["app_started"] = False

if not st.session_state["app_started"]:
    # =====================================================
    # LANDING PAGE (DARK MODE + CUSTOM CSS)
    # =====================================================
    st.markdown("""
        <style>
        /* Hide sidebar and header on landing page */
        [data-testid="collapsedControl"] {display: none;}
        header {display: none !important;}
        section[data-testid="stSidebar"] {display: none !important;}
        
        /* Hero Section Styling */
        .hero-container {
            text-align: center;
            padding: 10vh 20px 50px 20px;
            color: #E2E8F0;
        }
        .badge {
            display: inline-block;
            background: rgba(0, 255, 163, 0.1);
            color: #00FFA3;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            margin-bottom: 20px;
            border: 1px solid rgba(0, 255, 163, 0.3);
        }
        .hero-title {
            font-size: 4rem;
            font-weight: 800;
            line-height: 1.1;
            margin-bottom: 20px;
            background: -webkit-linear-gradient(#FFFFFF, #A0AEC0);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .hero-subtitle {
            font-size: 1.2rem;
            color: #A0AEC0;
            max-width: 600px;
            margin: 0 auto 40px auto;
            line-height: 1.5;
        }
        .feature-tags {
            display: flex;
            justify-content: center;
            gap: 15px;
            margin-top: 40px;
            flex-wrap: wrap;
        }
        .tag {
            background: #1E2128;
            padding: 8px 16px;
            border-radius: 8px;
            font-size: 12px;
            color: #CBD5E0;
            display: flex;
            align-items: center;
            gap: 8px;
            border: 1px solid #2D3748;
        }
        </style>

        <div class="hero-container">
            <div class="badge">• Sesuai Permen PU No. 18/PRT/M/2007</div>
            <h1 class="hero-title">Optimasi Jaringan Distribusi Air.<br>Tanpa Iterasi Manual.</h1>
            <p class="hero-subtitle">Upload file .inp EPANET, sistem menganalisis tekanan dan iterasi diameter secara otomatis, lalu download hasilnya.</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.write("") # Spacer
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Mulai Upload", type="primary", use_container_width=True):
                st.session_state["app_started"] = True
                st.rerun()
        with c2:
            st.button("Lihat Dokumentasi →", use_container_width=True)

    st.markdown("""
        <div class="feature-tags">
            <div class="tag">✓ Akurasi 100% EPANET engine</div>
            <div class="tag">✓ Efisien tidak berbelit</div>
            <div class="tag">✓ Output siap diekspor</div>
        </div>
    """, unsafe_allow_html=True)

else:
    # =====================================================
    # MAIN APP (UPLOADER & SOLVERS)
    # =====================================================
    st.sidebar.title("EPANET Pro Toolkit")
    st.sidebar.write("Pilih mode analisis:")

    menu = st.sidebar.radio(
        "Navigasi:",
        [
            "Auto-Solver (Engine: EPyT)",
            "Analisis Tekanan & Auto-PRV (Engine: WNTR)",
            "Analisis Loop (Metode Hardy Cross)"
        ]
    )

    st.sidebar.markdown("---")
    st.sidebar.info("Multi-engine: EPyT + WNTR")
    
    if st.sidebar.button("← Kembali ke Beranda"):
        st.session_state["app_started"] = False
        st.rerun()

    st.title(menu)

    uploaded_file = st.file_uploader(
        "Upload file .inp EPANET",
        type=["inp"]
    )

    # =====================================================
    # MAIN
    # =====================================================

    if uploaded_file is not None:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".inp") as tmp:
            tmp.write(uploaded_file.getvalue())
            tmp_path = tmp.name

        try:
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
