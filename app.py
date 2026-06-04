# app.py
from fastapi import FastAPI, UploadFile, File
import tempfile
import os
import solver

app = FastAPI(
    title="EPANET Solver API",
    description="API untuk analisis tekanan dan optimasi diameter pipa EPANET.",
    version="1.0.0"
)

@app.post("/api/analyze/pressure")
async def analyze_pressure_endpoint(file: UploadFile = File(...)):
    """
    Menerima unggahan file .inp, menganalisis tekanan pada t=0,
    dan mengembalikan metrik serta tabel tekanan junction dalam format JSON.
    """
    with tempfile.NamedTemporaryFile(delete=False, suffix=".inp") as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name
        
    try:
        results = solver.analyze_pressure(tmp_path)
        return results
    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        if os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except:
                pass

@app.post("/api/analyze/diameter")
async def analyze_diameter_endpoint(file: UploadFile = File(...)):
    """
    Menerima unggahan file .inp, menjalankan optimasi diameter pipa (sizing),
    dan mengembalikan metrik, tabel diameter baru, serta isi berkas .inp baru dalam format JSON.
    """
    with tempfile.NamedTemporaryFile(delete=False, suffix=".inp") as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name
        
    try:
        results = solver.optimize_diameter(tmp_path)
        # Hapus informasi path file lokal untuk keamanan
        if results and "inp_file_path" in results:
            # Hapus file final hasil optimasi jika ada di disk local
            final_path = results["inp_file_path"]
            if os.path.exists(final_path):
                try:
                    os.remove(final_path)
                except:
                    pass
            del results["inp_file_path"]
        return results
    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        if os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except:
                pass
