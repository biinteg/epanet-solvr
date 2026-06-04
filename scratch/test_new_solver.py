# scratch/test_new_solver.py
import sys
from unittest.mock import MagicMock
# Mock the entire wntr.sim package to prevent importing broken native modules
sys.modules['wntr.sim'] = MagicMock()
sys.modules['wntr.sim.core'] = MagicMock()
sys.modules['wntr.sim.aml'] = MagicMock()
sys.modules['wntr.sim.aml.evaluator'] = MagicMock()
sys.modules['wntr.sim.aml.aml'] = MagicMock()
sys.modules['wntr.sim.hydraulics'] = MagicMock()
sys.modules['wntr.sim.network_isolation'] = MagicMock()
sys.modules['wntr.sim.network_isolation.network_isolation'] = MagicMock()

import os
import shutil
import tempfile
import pandas as pd
import numpy as np
# pyrefly: ignore [missing-import]
from epyt import epanet

# Tambahkan project root ke sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.helpers import (
    MAX_HEADLOSS_M_PER_KM,
    MAX_VELOCITY_MS,
    MIN_VELOCITY_MS,
    MIN_PRESSURE_M,
)

standar_pipa = [50, 75, 100, 150, 200, 250, 300, 400, 500, 600, 800]
commercial_diameters = [d / 1000.0 for d in standar_pipa]

smaller_map = {commercial_diameters[i]: commercial_diameters[max(0, i-1)] for i in range(len(commercial_diameters))}
larger_map = {commercial_diameters[i]: commercial_diameters[min(len(commercial_diameters)-1, i+1)] for i in range(len(commercial_diameters))}

def snap_to_commercial(d):
    diffs = [abs(x - d) for x in commercial_diameters]
    return commercial_diameters[diffs.index(min(diffs))]

def run_auto_solver_generator(tmp_path):
    print("[1/5] Memuat model jaringan via EPyT...")
    from solver import clean_inp_file
    clean_inp_file(tmp_path)
    
    d = epanet(tmp_path)
    
    link_ids = d.getLinkNameID()
    node_ids = d.getNodeNameID()
    link_types = d.getLinkType()
    node_types = d.getNodeType()
    
    # Filter berdasarkan string type yang dikembalikan EPyT
    pipes = [link_ids[i] for i in range(len(link_ids)) if link_types[i].upper() == 'PIPE']
    junctions = [node_ids[i] for i in range(len(node_ids)) if node_types[i].upper() == 'JUNCTION']
    
    print(f"Pipa terdeteksi: {pipes}")
    print(f"Junction terdeteksi: {junctions}")
    
    original_diameters = {}
    lengths = {}
    link_nodes = d.getLinkNodesIndex()
    pipe_names_map = {}
    
    for i in range(len(link_ids)):
        name = link_ids[i]
        if name in pipes:
            original_diameters[name] = d.getLinkDiameter(i + 1)
            lengths[name] = d.getLinkLength(i + 1) # meter
            
            start_node_idx = link_nodes[i][0]
            end_node_idx = link_nodes[i][1]
            start_node_name = node_ids[start_node_idx - 1]
            end_node_name = node_ids[end_node_idx - 1]
            pipe_names_map[name] = f"Pipa {start_node_name} - {end_node_name}"
            
    lengths_series = pd.Series(lengths)
    lengths_clean = lengths_series.copy()
    lengths_clean[lengths_clean <= 0] = 1.0
    
    yield 0.05, "Jaringan pipa dimuat. Memulai simulasi awal..."
    
    def check_constraints(epanet_model):
        try:
            epanet_model.openHydraulicAnalysis()
            epanet_model.runHydraulicAnalysis()
            epanet_model.closeHydraulicAnalysis()
            
            raw_pressures = epanet_model.getNodePressure()
            raw_velocities = epanet_model.getLinkVelocity()
            raw_headloss = epanet_model.getLinkHeadloss()
            
            # Ubah output array numpy ke pandas Series dengan index nama
            pressures = pd.Series(raw_pressures, index=node_ids).loc[junctions]
            velocities = pd.Series(raw_velocities, index=link_ids).loc[pipes].abs()
            
            hl_gradients = pd.Series(raw_headloss, index=link_ids).loc[pipes].abs()
            headloss_totals = hl_gradients * (lengths_series / 1000.0)
            
            min_p_global = pressures.min()
            is_safe = (min_p_global >= MIN_PRESSURE_M)
            
            return {
                "success": True,
                "is_safe": is_safe,
                "min_p": min_p_global,
                "pressures": pressures,
                "velocities": velocities,
                "hl_gradients": hl_gradients,
                "headloss_totals": headloss_totals
            }
        except Exception as e:
            return {
                "success": False,
                "is_safe": False,
                "min_p": -999.0,
                "pressures": pd.Series(0.0, index=junctions),
                "velocities": pd.Series(99.0, index=pipes),
                "hl_gradients": pd.Series(999.0, index=pipes),
                "headloss_totals": pd.Series(999.0, index=pipes),
                "error": str(e)
            }

    for name in pipes:
        idx = link_ids.index(name) + 1
        d_val = d.getLinkDiameter(idx)
        d.setLinkDiameter(idx, snap_to_commercial(d_val / 1000.0) * 1000.0)
        
    yield 0.1, "Menjalankan optimasi kelayakan awal (Fase 1)..."
    for iter_f1 in range(5):
        eval_res = check_constraints(d)
        if not eval_res["success"]:
            for name in pipes:
                idx = link_ids.index(name) + 1
                d_now = d.getLinkDiameter(idx) / 1000.0
                d.setLinkDiameter(idx, larger_map[d_now] * 1000.0)
            continue
            
        v = eval_res["velocities"]
        hl_grad = eval_res["hl_gradients"]
        
        changed = False
        for name in pipes:
            idx = link_ids.index(name) + 1
            d_now = d.getLinkDiameter(idx) / 1000.0
            
            if v[name] > MAX_VELOCITY_MS or hl_grad[name] > MAX_HEADLOSS_M_PER_KM:
                d_new = larger_map[d_now]
            elif v[name] < MIN_VELOCITY_MS:
                d_new = smaller_map[d_now]
            else:
                d_new = d_now
                
            if d_new != d_now:
                d.setLinkDiameter(idx, d_new * 1000.0)
                changed = True
                
        if not changed:
            break
            
        yield 0.1 + (iter_f1 / 5.0) * 0.2, f"Iterasi Kelayakan {iter_f1 + 1}/5 selesai."
        
    eval_res = check_constraints(d)
    
    if not eval_res["is_safe"]:
        yield 0.35, "Tekanan awal tidak aman. Memperbesar pipa bottleneck..."
        sorted_pipes_by_hl = eval_res["headloss_totals"].sort_values(ascending=False).index.tolist()
        for name in sorted_pipes_by_hl:
            idx = link_ids.index(name) + 1
            d_now = d.getLinkDiameter(idx) / 1000.0
            if d_now == commercial_diameters[-1]:
                continue
            d.setLinkDiameter(idx, larger_map[d_now] * 1000.0)
            test_res = check_constraints(d)
            if test_res["is_safe"] or test_res["min_p"] > eval_res["min_p"]:
                eval_res = test_res
                if eval_res["is_safe"]:
                    yield 0.45, "Tekanan berhasil dipulihkan ke batas aman!"
                    break
            else:
                d.setLinkDiameter(idx, d_now * 1000.0)
                
    yield 0.5, "Mengecilkan pipa non-sensitif secara masal (Batch Shrinking)..."
    insensitive_pipes = []
    for name in pipes:
        idx = link_ids.index(name) + 1
        d_now = d.getLinkDiameter(idx) / 1000.0
        if d_now > commercial_diameters[0] and eval_res["headloss_totals"][name] < 0.05:
            insensitive_pipes.append(name)
            
    if insensitive_pipes:
        backup_diams = {name: d.getLinkDiameter(link_ids.index(name) + 1) / 1000.0 for name in insensitive_pipes}
        for name in insensitive_pipes:
            idx = link_ids.index(name) + 1
            d.setLinkDiameter(idx, smaller_map[backup_diams[name]] * 1000.0)
            
        test_res = check_constraints(d)
        if test_res["is_safe"] and (test_res["velocities"] <= MAX_VELOCITY_MS).all() and (test_res["hl_gradients"] <= MAX_HEADLOSS_M_PER_KM).all():
            eval_res = test_res
            yield 0.6, f"Batch-shrinking berhasil menghemat diameter {len(insensitive_pipes)} pipa!"
        else:
            for name in insensitive_pipes:
                idx = link_ids.index(name) + 1
                d.setLinkDiameter(idx, backup_diams[name] * 1000.0)
            yield 0.6, "Batch-shrinking melanggar batas keamanan. Lanjut ke evaluasi individu..."
            
    yield 0.65, "Memulai optimasi biaya pipa individu..."
    sorted_pipes_ascending = eval_res["headloss_totals"].sort_values(ascending=True).index.tolist()
    
    for idx, name in enumerate(sorted_pipes_ascending):
        link_idx = link_ids.index(name) + 1
        d_now = d.getLinkDiameter(link_idx) / 1000.0
        if d_now <= commercial_diameters[0]:
            continue
            
        margin = eval_res["min_p"] - MIN_PRESSURE_M
        if margin < 0.05 and eval_res["hl_gradients"][name] > 0.5:
            continue
            
        d_try = smaller_map[d_now]
        d.setLinkDiameter(link_idx, d_try * 1000.0)
        test_res = check_constraints(d)
        
        is_velocity_ok = test_res["velocities"][name] <= MAX_VELOCITY_MS
        is_hl_ok = test_res["hl_gradients"][name] <= MAX_HEADLOSS_M_PER_KM
        is_pressure_ok = test_res["is_safe"]
        
        if test_res["success"] and is_velocity_ok and is_hl_ok and is_pressure_ok:
            eval_res = test_res
        else:
            d.setLinkDiameter(link_idx, d_now * 1000.0)
            
        progress = 0.65 + (idx / len(sorted_pipes_ascending)) * 0.3
        yield progress, f"Optimasi pipa {idx+1}/{len(sorted_pipes_ascending)} ({name}) selesai."
        
    yield 0.95, "Optimasi selesai. Menyusun file hasil..."
    
    new_inp = tmp_path.replace(".inp", "_optimized.inp")
    d.saveInputFile(new_inp)
    d.unload()
    
    d_final = epanet(new_inp)
    final_results = check_constraints(d_final)
    
    hasil = []
    berubah = 0
    patuh = 0
    for name in pipes:
        link_idx = link_ids.index(name) + 1
        awal = original_diameters[name]
        akhir = d_final.getLinkDiameter(link_idx)
        v_val = final_results["velocities"][name]
        hl_val = final_results["hl_gradients"][name]
        
        nodes = link_nodes[link_idx - 1]
        end_node_name = node_ids[nodes[1] - 1]
        p_hilir_val = final_results["pressures"].get(end_node_name, 0.0)
        
        sesuai_permen = MIN_VELOCITY_MS <= v_val <= MAX_VELOCITY_MS and hl_val <= MAX_HEADLOSS_M_PER_KM
        status = "Diperbesar" if akhir > awal else "Diperkecil" if akhir < awal else "Tetap"
        
        if awal != akhir: berubah += 1
        if sesuai_permen: patuh += 1
        
        hasil.append({
            "ID": name,
            "Nama Pipa": pipe_names_map.get(name, f"Pipa {name}"),
            "Diameter Awal": f"{awal:.0f} mm",
            "Diameter Baru": f"{akhir:.0f} mm",
            "Velocity": f"{v_val:.3f} m/s",
            "Headloss": f"{hl_val:.3f} m/km",
            "Pressure": f"{p_hilir_val:.1f} m",
            "Status": status,
            "Compliance": "Aman" if sesuai_permen else "Tidak Aman"
        })
        
    d_final.unload()
    
    # Bersihkan file hasil optimasi sebelum WNTR membaca untuk rename link
    from solver import clean_inp_file
    clean_inp_file(new_inp)
    
    from modules.helpers import rename_inp_links
    final_inp = tmp_path.replace(".inp", "_final.inp")
    if rename_inp_links(new_inp, final_inp):
        if os.path.exists(new_inp): os.remove(new_inp)
    else:
        final_inp = new_inp
        
    df = pd.DataFrame(hasil)
    output = {
        "type": "auto_solver",
        "df": df,
        "metrics": {
            "total": len(pipes),
            "changed": berubah,
            "compliant": patuh
        },
        "inp_file_path": final_inp
    }
    yield 1.0, output

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    test_inp_orig = os.path.join(base_dir, "scratch", "test.inp")
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".inp") as tmp:
        with open(test_inp_orig, 'rb') as f:
            tmp.write(f.read())
        tmp_path = tmp.name
        
    try:
        print("Starting EPyT solver generator test with full sim mocks...")
        generator = run_auto_solver_generator(tmp_path)
        final_res = None
        for progress, val in generator:
            print(f"[{progress*100:.0f}%] {val if isinstance(val, str) else 'Result Dict Generated'}")
            if isinstance(val, dict):
                final_res = val
                
        print("\nOptimization complete! Metrics:")
        print(final_res["metrics"])
        print("\nResults DataFrame:")
        print(final_res["df"].to_string())
        print(f"\nFinal Optimized INP Path: {final_res['inp_file_path']}")
        
    finally:
        if os.path.exists(tmp_path): os.remove(tmp_path)
        final_file = tmp_path.replace(".inp", "_final.inp")
        if os.path.exists(final_file): os.remove(final_file)
