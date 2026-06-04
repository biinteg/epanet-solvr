# scratch/test_modular.py
import sys
import os
import shutil
import tempfile
import pandas as pd

# Mock WNTR before importing helpers to prevent C++ compiler crash
from unittest.mock import MagicMock
sys.modules['wntr.sim.aml._evaluator'] = MagicMock()
sys.modules['wntr.sim.network_isolation._network_isolation'] = MagicMock()
sys.modules['wntr.sim'] = MagicMock()
sys.modules['wntr.sim.core'] = MagicMock()
sys.modules['wntr.sim.aml'] = MagicMock()
sys.modules['wntr.sim.aml.evaluator'] = MagicMock()
sys.modules['wntr.sim.aml.aml'] = MagicMock()
sys.modules['wntr.sim.hydraulics'] = MagicMock()
sys.modules['wntr.sim.network_isolation'] = MagicMock()
sys.modules['wntr.sim.network_isolation.network_isolation'] = MagicMock()

# Tambahkan path project root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import solver
from app import app
# pyrefly: ignore [missing-import]
from fastapi.testclient import TestClient

def test_local_solver(tmp_path):
    print("--- MENGETES SOLVER LOKAL ---")
    
    # 1. Tes analyze_pressure
    print("Mengetes analyze_pressure...")
    p_results = solver.analyze_pressure(tmp_path)
    print("Metrik Tekanan:", p_results["metrics"])
    print("Data Tekanan (2 baris awal):", p_results["table"][:2])
    
    # 2. Tes optimize_diameter
    print("Mengetes optimize_diameter...")
    d_results = solver.optimize_diameter(tmp_path)
    print("Metrik Diameter:", d_results["metrics"])
    print("Data Diameter (2 baris awal):", d_results["table"][:2])
    print("Ukuran File Optimized INP:", len(d_results["optimized_inp_content"]), "karakter")

def test_fastapi_endpoints(tmp_path):
    print("\n--- MENGETES ENDPOINT FASTAPI ---")
    client = TestClient(app)
    
    # 1. Tes POST /api/analyze/pressure
    print("Mengetes POST /api/analyze/pressure...")
    with open(tmp_path, "rb") as f:
        response = client.post("/api/analyze/pressure", files={"file": ("test.inp", f, "text/plain")})
    
    assert response.status_code == 200, f"Error: status code {response.status_code}"
    data = response.json()
    print("Response JSON Keys:", list(data.keys()))
    print("Metrik dari API:", data.get("metrics"))
    
    # 2. Tes POST /api/analyze/diameter
    print("Mengetes POST /api/analyze/diameter...")
    with open(tmp_path, "rb") as f:
        response = client.post("/api/analyze/diameter", files={"file": ("test.inp", f, "text/plain")})
        
    assert response.status_code == 200, f"Error: status code {response.status_code}"
    data = response.json()
    print("Response JSON Keys:", list(data.keys()))
    print("Metrik dari API:", data.get("metrics"))
    print("Panjang berkas optimized hasil API:", len(data.get("optimized_inp_content", "")))

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    test_inp_orig = os.path.join(base_dir, "scratch", "test.inp")
    
    # Buat temp file agar tidak menimpa file test asli
    with tempfile.NamedTemporaryFile(delete=False, suffix=".inp") as tmp:
        with open(test_inp_orig, 'rb') as f:
            tmp.write(f.read())
        tmp_path = tmp.name
        
    try:
        # Jalankan tes lokal
        test_local_solver(tmp_path)
        
        # Jalankan tes API
        test_fastapi_endpoints(tmp_path)
        
        print("\n=== SEMUA TES BERHASIL LOLOS! ===")
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        
        # Hapus temp file yang dihasilkan dari optimasi
        opt_temp = tmp_path.replace(".inp", "_optimized.inp")
        if os.path.exists(opt_temp): os.remove(opt_temp)
        fin_temp = tmp_path.replace(".inp", "_final.inp")
        if os.path.exists(fin_temp): os.remove(fin_temp)
