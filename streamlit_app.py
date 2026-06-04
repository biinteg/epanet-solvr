# streamlit_app.py
# pyrefly: ignore [missing-import]
import streamlit as st
# pyrefly: ignore [missing-import]
import requests
import pandas as pd
import io

# =====================================================
# PAGE CONFIG & PREMIUM STYLING
# =====================================================
st.set_page_config(
    page_title="EPANET Cloud Client",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Premium CSS (Glassmorphism & Dark Mode)
st.markdown("""
<style>
    /* Global Background & Dark Theme */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
        color: #f8fafc;
        font-family: 'Inter', -apple-system, sans-serif;
    }
    
    /* Header Card */
    .header-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px rgba(255, 255, 255, 0.05) solid;
        border-radius: 16px;
        padding: 32px;
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        margin-bottom: 24px;
        border-left: 5px solid #00f2fe;
    }
    
    .header-title {
        font-size: 36px;
        font-weight: 800;
        background: linear-gradient(to right, #00f2fe, #4facfe);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 8px;
    }
    
    .header-subtitle {
        color: #94a3b8;
        font-size: 16px;
        margin: 0;
    }
    
    /* Metric Card Custom */
    .metric-card {
        background: rgba(255, 255, 255, 0.02);
        border: 1px rgba(255, 255, 255, 0.05) solid;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 4px 16px 0 rgba(0, 0, 0, 0.2);
    }
    
    .metric-val {
        font-size: 32px;
        font-weight: 800;
        color: #00f2fe;
    }
    
    .metric-label {
        color: #94a3b8;
        font-size: 14px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #0b0f19 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
</style>
""", unsafe_allow_html=True)

# =====================================================
# SIDEBAR CONFIGURATION
# =====================================================
st.sidebar.markdown("### ⚙️ Server Configuration")
backend_url = st.sidebar.text_input(
    "URL Backend API",
    value="http://localhost:8000",
    help="Ubah ke URL deployment Railway atau Render Anda"
)

st.sidebar.markdown("---")
st.sidebar.markdown("""
### ℹ️ Informasi
Aplikasi ini berjalan dalam mode **Decoupled**. 
Semua simulasi WNTR & EPyT dijalankan di server eksternal berkinerja tinggi, sehingga aplikasi web frontend tetap ringan, cepat, dan hemat memori.
""")

# Tombol Cek Status Server
if st.sidebar.button("Cek Koneksi Server 🔌", use_container_width=True):
    try:
        # Coba ping docs endpoint untuk verifikasi
        response = requests.get(f"{backend_url}/docs", timeout=5)
        if response.status_code == 200:
            st.sidebar.success("Koneksi berhasil! Server aktif.")
        else:
            st.sidebar.warning(f"Server merespons dengan status: {response.status_code}")
    except requests.exceptions.RequestException as e:
        st.sidebar.error("Gagal terhubung ke backend server. Periksa URL atau hidupkan server.")

# =====================================================
# MAIN DASHBOARD AREA
# =====================================================
st.markdown("""
<div class="header-card">
    <h1 class="header-title">EPANET Decoupled Dashboard</h1>
    <p class="header-subtitle">
        Analisis tekanan baseline dan optimasi otomatis ukuran diameter pipa melalui REST API Serverless.
    </p>
</div>
""", unsafe_allow_html=True)

# file uploader .inp
uploaded_file = st.file_uploader("Unggah file konfigurasi jaringan EPANET (.inp)", type=["inp"])

if uploaded_file is not None:
    # Simpan file di memory
    file_bytes = uploaded_file.getvalue()
    
    st.markdown("### 🛠️ Pilih Metode Analisis")
    col_btn1, col_btn2 = st.columns(2)
    
    with col_btn1:
        tombol_tekanan = st.button("💧 Analisis Tekanan Baseline", type="primary", use_container_width=True)
    with col_btn2:
        tombol_diameter = st.button("⚡ Optimasi Diameter Pipa", type="primary", use_container_width=True)
        
    # LOGIKA TOMBOL 1: ANALISIS TEKANAN
    if tombol_tekanan:
        st.info("Mengirim data jaringan ke backend server untuk analisis tekanan...")
        
        try:
            # Kirim file inp via HTTP POST
            files = {"file": (uploaded_file.name, file_bytes, "text/plain")}
            response = requests.post(f"{backend_url}/api/analyze/pressure", files=files, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success", False):
                    metrics = result["metrics"]
                    table = result["table"]
                    df = pd.DataFrame(table)
                    
                    st.success("Analisis tekanan selesai dilakukan!")
                    
                    # Tampilkan metrik
                    col_m1, col_m2, col_m3 = st.columns(3)
                    with col_m1:
                        st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-val">{metrics['total']}</div>
                            <div class="metric-label">Total Junction</div>
                        </div>
                        """, unsafe_allow_html=True)
                    with col_m2:
                        st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-val" style="color: #ff4b4b;">{metrics['low']}</div>
                            <div class="metric-label">Tekanan Rendah (<10m)</div>
                        </div>
                        """, unsafe_allow_html=True)
                    with col_m3:
                        st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-val" style="color: #ffa500;">{metrics['high']}</div>
                            <div class="metric-label">Tekanan Tinggi (>80m)</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Tampilkan Dataframe tekanan
                    st.markdown("### 📊 Tabel Tekanan Junction (t=0)")
                    
                    def warna_status(val):
                        if val == "Aman":
                            return "background-color: rgba(46, 204, 113, 0.1); color: #2ecc71; font-weight: bold;"
                        elif val == "Terlalu Rendah":
                            return "background-color: rgba(231, 76, 60, 0.1); color: #e74c3c; font-weight: bold;"
                        else:
                            return "background-color: rgba(243, 156, 18, 0.1); color: #f39c12; font-weight: bold;"
                            
                    st.dataframe(df.style.map(warna_status, subset=["Status"]), use_container_width=True)
                else:
                    st.error(f"Gagal memproses file di backend: {result.get('error', 'Unknown Error')}")
            else:
                st.error(f"Gagal melakukan request ke backend API. HTTP Status Code: {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            st.error(f"Gagal terhubung ke server backend di {backend_url}. Pastikan server aktif dan URL yang Anda masukkan sudah benar.")
        except Exception as e:
            st.error(f"Terjadi kesalahan yang tidak terduga: {str(e)}")
            
    # LOGIKA TOMBOL 2: OPTIMASI DIAMETER
    if tombol_diameter:
        st.info("Mengirim data jaringan ke backend server untuk optimasi diameter...")
        
        try:
            # Kirim file inp via HTTP POST
            files = {"file": (uploaded_file.name, file_bytes, "text/plain")}
            response = requests.post(f"{backend_url}/api/analyze/diameter", files=files, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                if result.get("type") == "auto_solver":
                    metrics = result["metrics"]
                    table = result["table"]
                    df = pd.DataFrame(table)
                    optimized_content = result.get("optimized_inp_content", "")
                    
                    st.success("Optimasi diameter pipa selesai dilakukan!")
                    
                    # Tampilkan metrik
                    col_d1, col_d2, col_d3 = st.columns(3)
                    with col_d1:
                        st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-val">{metrics['total']}</div>
                            <div class="metric-label">Total Pipa</div>
                        </div>
                        """, unsafe_allow_html=True)
                    with col_d2:
                        st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-val" style="color: #2ecc71;">{metrics['changed']}</div>
                            <div class="metric-label">Pipa Berubah</div>
                        </div>
                        """, unsafe_allow_html=True)
                    with col_d3:
                        st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-val" style="color: #00f2fe;">{metrics['compliant']}</div>
                            <div class="metric-label">Pipa Patuh Kriteria</div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                    # Tampilkan Dataframe diameter baru
                    st.markdown("### 📊 Tabel Hasil Optimasi Diameter Pipa")
                    
                    def warna_status_diameter(val):
                        if val == "Diperbesar":
                            return "background-color: rgba(46, 204, 113, 0.1); color: #2ecc71; font-weight: bold;"
                        elif val == "Diperkecil":
                            return "background-color: rgba(243, 156, 18, 0.1); color: #f39c12; font-weight: bold;"
                        else:
                            return "background-color: rgba(52, 152, 219, 0.1); color: #3498db; font-weight: bold;"
                            
                    st.dataframe(df.style.map(warna_status_diameter, subset=["Status"]), use_container_width=True)
                    
                    # Download button berkas optimized
                    if optimized_content:
                        st.download_button(
                            label="📥 DOWNLOAD BERKAS HASIL OPTIMASI (.inp)",
                            data=optimized_content,
                            file_name="Optimized_Network.inp",
                            mime="text/plain",
                            use_container_width=True
                        )
                else:
                    st.error(f"Gagal memproses file di backend: {result.get('error', 'Format hasil salah')}")
            else:
                st.error(f"Gagal melakukan request ke backend API. HTTP Status Code: {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            st.error(f"Gagal terhubung ke server backend di {backend_url}. Pastikan server aktif dan URL yang Anda masukkan sudah benar.")
        except Exception as e:
            st.error(f"Terjadi kesalahan yang tidak terduga: {str(e)}")
else:
    st.info("Silakan unggah berkas .inp terlebih dahulu untuk memulai analisis.")
