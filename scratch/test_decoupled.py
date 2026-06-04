# scratch/test_decoupled.py
import sys
import os
import time
import subprocess
import requests
import tempfile

# Tambahkan path project root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def run_decoupled_test():
    print("=== MEMULAI PENGUJIAN INTEGRASI DECOUPLED ===")
    
    # Port khusus untuk testing
    port = "8089"
    backend_url = f"http://127.0.0.1:{port}"
    
    # 1. Jalankan FastAPI server menggunakan subprocess uvicorn
    print(f"Menjalankan server backend FastAPI via uvicorn pada port {port}...")
    
    # Gunakan python interpreter yang sama dengan lingkungan aktif
    python_exe = sys.executable
    process = subprocess.Popen(
        [python_exe, "-m", "uvicorn", "main:app", "--port", port, "--host", "127.0.0.1"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Berikan jeda waktu agar uvicorn siap menerima request
    print("Menunggu server booting (3 detik)...")
    time.sleep(3)
    
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    test_inp_orig = os.path.join(base_dir, "scratch", "test.inp")
    
    # Gunakan temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".inp") as tmp:
        with open(test_inp_orig, 'rb') as f:
            tmp.write(f.read())
        tmp_path = tmp.name
        
    try:
        # Cek apakah server merespons
        print("Mengecek endpoint /docs...")
        r_ping = requests.get(f"{backend_url}/docs", timeout=5)
        assert r_ping.status_code == 200, f"Gagal ping server. Status code: {r_ping.status_code}"
        print("Server aktif!")
        
        # 2. Tes POST /api/analyze/pressure
        print("\n[UJI 1] Mengirim request ke /api/analyze/pressure...")
        with open(tmp_path, "rb") as f:
            files = {"file": (os.path.basename(tmp_path), f, "text/plain")}
            response = requests.post(f"{backend_url}/api/analyze/pressure", files=files, timeout=15)
            
        assert response.status_code == 200, f"Error: status code {response.status_code}"
        res_json = response.json()
        print("Keys yang diterima:", list(res_json.keys()))
        print("Metrik Tekanan dari API:", res_json.get("metrics"))
        print("Total Baris Tekanan:", len(res_json.get("table", [])))
        print("Response JSON:", res_json)
        assert res_json.get("success") is True, f"Pengujian pressure gagal: {res_json.get('error')}"
        
        # 3. Tes POST /api/analyze/diameter
        print("\n[UJI 2] Mengirim request ke /api/analyze/diameter...")
        with open(tmp_path, "rb") as f:
            files = {"file": (os.path.basename(tmp_path), f, "text/plain")}
            response = requests.post(f"{backend_url}/api/analyze/diameter", files=files, timeout=25)
            
        assert response.status_code == 200, f"Error: status code {response.status_code}"
        res_json = response.json()
        print("Keys yang diterima:", list(res_json.keys()))
        print("Metrik Diameter dari API:", res_json.get("metrics"))
        print("Total Baris Diameter:", len(res_json.get("table", [])))
        print("Panjang berkas optimized:", len(res_json.get("optimized_inp_content", "")))
        assert res_json.get("type") == "auto_solver", "Pengujian diameter gagal."
        
        print("\n=== KEDUA ENDPOINT DECOUPLED BERHASIL DIUJI DAN LOLOS 100% ===")
        
    except Exception as e:
        print(f"\n[ERROR] TERJADI KESALAHAN SAAT TESTING: {e}")
        # Print stdout/stderr uvicorn jika error
        stdout, stderr = process.communicate(timeout=1)
        print("--- SERVER STDOUT ---")
        print(stdout)
        print("--- SERVER STDERR ---")
        print(stderr)
        raise e
    finally:
        # Hentikan server subprocess
        print("\nMematikan server uvicorn...")
        process.terminate()
        process.wait()
        print("Server dinonaktifkan.")
        
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
            
        # Bersihkan file temp optimasi hasil solver
        opt_temp = tmp_path.replace(".inp", "_optimized.inp")
        if os.path.exists(opt_temp): os.remove(opt_temp)
        fin_temp = tmp_path.replace(".inp", "_final.inp")
        if os.path.exists(fin_temp): os.remove(fin_temp)

if __name__ == "__main__":
    run_decoupled_test()
