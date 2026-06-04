# main.py
import sys
from unittest.mock import MagicMock
try:
    import wntr
except (ImportError, ModuleNotFoundError):
    # Mock parsial hanya untuk sim biner WNTR agar import berhasil di Python 3.14
    sys.modules['wntr.sim.aml._evaluator'] = MagicMock()
    sys.modules['wntr.sim.network_isolation._network_isolation'] = MagicMock()
    sys.modules['wntr.sim.network_isolation.network_isolation'] = MagicMock()
    sys.modules['wntr.sim.aml.evaluator'] = MagicMock()
    import wntr

from fastapi import FastAPI, UploadFile, File
import tempfile
import os
import pandas as pd
# pyrefly: ignore [missing-import]
from epyt import epanet
import solver

app = FastAPI(
    title="EPANET Decoupled Backend API",
    description="Backend API untuk analisis tekanan dan optimasi diameter pipa EPANET.",
    version="2.0.0"
)

@app.post("/api/analyze/pressure")
async def analyze_pressure_endpoint(file: UploadFile = File(...)):
    """
    Menerima file .inp, menjalankan simulasi dengan WNTR EpanetSimulator,
    dan mengembalikan tekanan & demand pada t=0.
    Jika WNTR mengalami kendala dependency, otomatis beralih menggunakan EPyT.
    """
    with tempfile.NamedTemporaryFile(delete=False, suffix=".inp") as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name
        
    try:
        # Bersihkan file dari tag leakage/backflow agar WNTR tidak error
        solver.clean_inp_file(tmp_path)
        
        # Coba gunakan WNTR EpanetSimulator
        use_wntr = False
        results = None
        wn = None
        try:
            import wntr
            # Memvalidasi jika WNTR bukan mock dan simulator bisa berjalan
            wn = wntr.network.WaterNetworkModel(tmp_path)
            sim = wntr.sim.EpanetSimulator(wn)
            results = sim.run_sim()
            use_wntr = True
        except Exception as wntr_err:
            print(f"[Backend Log] WNTR simulator failed or not available ({wntr_err}). Using EPyT fallback...")
            use_wntr = False
            
        if use_wntr and results is not None:
            # Menggunakan hasil WNTR
            tekanan_awal = results.node["pressure"].iloc[0]
            demand_awal = results.node["demand"].iloc[0]
            junctions = list(wn.junction_name_list)
            
            data = []
            low_p = 0
            high_p = 0
            
            for node in junctions:
                p = tekanan_awal[node]
                d = demand_awal[node]
                
                # Antisipasi nilai absurd
                p = 0.0 if (pd.isna(p) or p < -100) else p
                d = 0.0 if pd.isna(d) else d
                
                if p < solver.MIN_PRESSURE_M:
                    status = "Terlalu Rendah"
                    low_p += 1
                elif p > solver.MAX_PRESSURE_M:
                    status = "Bahaya (Terlalu Tinggi)"
                    high_p += 1
                else:
                    status = "Aman"
                    
                data.append({
                    "Node": node,
                    "Tekanan": float(round(p, 2)),
                    "Demand": float(round(d, 4)),
                    "Status": status
                })
        else:
            # Fallback menggunakan EPyT
            d_epyt = epanet(tmp_path)
            try:
                node_ids = d_epyt.getNodeNameID()
                node_types = d_epyt.getNodeType()
                
                # Filter junction (tipe 'JUNCTION')
                junctions = [node_ids[i] for i in range(len(node_ids)) if node_types[i].upper() == 'JUNCTION']
                
                d_epyt.openHydraulicAnalysis()
                d_epyt.runHydraulicAnalysis()
                d_epyt.closeHydraulicAnalysis()
                
                raw_pressures = d_epyt.getNodePressure()
                pressures_dict = {node_ids[i]: raw_pressures[i] for i in range(len(node_ids))}
                
                # Ambil base demands dari EPyT
                raw_demands = d_epyt.getNodeBaseDemands()
                # Category 1 biasanya index pertama (nilai default)
                base_demands = raw_demands.get(1, [0.0] * len(node_ids))
                demands_dict = {node_ids[i]: base_demands[i] for i in range(len(node_ids))}
                
                data = []
                low_p = 0
                high_p = 0
                
                for node in junctions:
                    p = pressures_dict.get(node, 0.0)
                    d = demands_dict.get(node, 0.0)
                    
                    p = 0.0 if (pd.isna(p) or p < -100) else p
                    d = 0.0 if pd.isna(d) else d
                    
                    if p < solver.MIN_PRESSURE_M:
                        status = "Terlalu Rendah"
                        low_p += 1
                    elif p > solver.MAX_PRESSURE_M:
                        status = "Bahaya (Terlalu Tinggi)"
                        high_p += 1
                    else:
                        status = "Aman"
                        
                    data.append({
                        "Node": node,
                        "Tekanan": float(round(p, 2)),
                        "Demand": float(round(d, 4)),
                        "Status": status
                    })
            finally:
                d_epyt.unload()
                
        return {
            "success": True,
            "metrics": {
                "low": int(low_p),
                "high": int(high_p),
                "total": int(len(junctions))
            },
            "table": data
        }
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
    Menerima file .inp, menjalankan logika optimasi diameter pipa dari solver.py,
    dan mengembalikan metrik, tabel hasil, serta isi berkas hasil optimasi.
    """
    with tempfile.NamedTemporaryFile(delete=False, suffix=".inp") as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name
        
    try:
        results = solver.optimize_diameter(tmp_path)
        # Bersihkan path lokal untuk keamanan server
        if results and "inp_file_path" in results:
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
