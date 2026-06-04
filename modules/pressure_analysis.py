import os
# pyrefly: ignore [missing-import]
import streamlit as st
# pyrefly: ignore [missing-import]
import wntr
# pyrefly: ignore [missing-import]
import pandas as pd
from datetime import datetime, timezone
from itertools import combinations
from modules.helpers import (
    MAX_PRESSURE_M,
    MIN_PRESSURE_M,
    warnai_status_tekanan,
    tampilkan_network,
)

def run_pressure_analysis(tmp_path, target_prv=50.0, run_triple_prv=False):
    """
    Runs pressure analysis and optionally searches for Triple PRV combination.
    Returns diagnostic data and results.
    """
    # Clean file (boilerplate for EPANET compatibility)
    with open(tmp_path, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()
    with open(tmp_path, "w", encoding="utf-8") as f:
        skip = False
        for line in lines:
            u = line.strip().upper()
            if u == "[LEAKAGE]": skip = True; continue
            if skip and line.startswith("["): skip = False
            if "BACKFLOW ALLOWED" in u: continue
            if not skip: f.write(line)

    wn = wntr.network.WaterNetworkModel(tmp_path)
    sim = wntr.sim.EpanetSimulator(wn)
    results = sim.run_sim()
    tekanan_awal = results.node["pressure"].iloc[0]

    data_awal = []
    low_p = 0; high_p = 0
    for node in wn.junction_name_list:
        p = tekanan_awal[node]
        p = 0 if (pd.isna(p) or p < -100) else p
        if p < MIN_PRESSURE_M: status = "Terlalu Rendah"; low_p += 1
        elif p > MAX_PRESSURE_M: status = "Bahaya (Terlalu Tinggi)"; high_p += 1
        else: status = "Aman"
        data_awal.append({"Node": node, "Tekanan": round(p, 2), "Status": status})

    df_awal = pd.DataFrame(data_awal)
    
    output = {
        "type": "pressure",
        "df_awal": df_awal,
        "metrics_awal": {"low": low_p, "high": high_p, "total": len(wn.junction_name_list)},
        "wn_initial": wn,
        "tekanan_awal": tekanan_awal
    }

    if run_triple_prv:
        # Determine candidate pipes dynamically using various thresholds.
        thresholds = [0.15, 0.10, 0.05, 0.0]
        kandidat_pipa = []
        for threshold in thresholds:
            kandidat_pipa = [p for p in wn.pipe_name_list if wn.get_link(p).diameter > threshold]
            if len(kandidat_pipa) >= 3:
                break
        
        if not kandidat_pipa:
            kandidat_pipa = list(wn.pipe_name_list)

        # Generate combinations of size 0, 1, 2, and 3
        combos = [()]
        max_prvs_to_add = min(len(kandidat_pipa), 3)
        for r in range(1, max_prvs_to_add + 1):
            combos.extend(combinations(kandidat_pipa, r))

        best_score = -999999; best_combo = None; best_result = {}; best_network = None
        best_aman = 0; best_high = 0; best_low = 0

        for combo in combos:
            try:
                wn_test = wntr.network.WaterNetworkModel(tmp_path)
                
                # Update all existing PRVs to target_prv
                for valve_name in wn_test.valve_name_list:
                    valve = wn_test.get_link(valve_name)
                    if getattr(valve, 'valve_type', '') == 'PRV':
                        valve.initial_setting = target_prv
                
                # Add new PRVs by replacing selected pipes
                for pipe_name in combo:
                    pipe = wn_test.get_link(pipe_name)
                    wn_test.remove_link(pipe_name)
                    wn_test.add_valve(f"PRV_{pipe_name}", pipe.start_node_name, pipe.end_node_name, 
                                    diameter=pipe.diameter, valve_type="PRV", initial_setting=target_prv)
                
                sim_test = wntr.sim.EpanetSimulator(wn_test)
                res = sim_test.run_sim()
                tekanan_series = res.node["pressure"]
                tekanan = tekanan_series.max()
                
                if any(pd.isna(tekanan[n]) or tekanan[n] < -100 for n in wn_test.junction_name_list):
                    continue
                    
                aman = sum(1 for n in wn_test.junction_name_list if MIN_PRESSURE_M <= tekanan[n] <= MAX_PRESSURE_M)
                high_count = sum(1 for n in wn_test.junction_name_list if tekanan[n] > MAX_PRESSURE_M)
                low_count = sum(1 for n in wn_test.junction_name_list if tekanan[n] < MIN_PRESSURE_M)
                
                # Scoring: maximize safe nodes, penalize high pressures slightly, penalize low pressures heavily
                score = aman * 100 - high_count * 2 - low_count * 5
                
                if score > best_score:
                    best_score = score
                    best_combo = combo
                    best_result = tekanan
                    best_network = wn_test
                    best_aman = aman
                    best_high = high_count
                    best_low = low_count
            except:
                continue

        if best_network is not None:
            compare = []
            for node in wn.junction_name_list:
                new_p = best_result[node]
                p_tampil = new_p if (pd.notna(new_p) and new_p > -100) else 0
                status = "Terlalu Rendah" if p_tampil < MIN_PRESSURE_M else "Bahaya (Terlalu Tinggi)" if p_tampil > MAX_PRESSURE_M else "Aman"
                compare.append({"Node": node, "Tekanan Sebelum": round(tekanan_awal[node], 2), "Tekanan Sesudah": round(p_tampil, 2), "Status": status})
            
            prv_temp = tmp_path.replace(".inp", "_PRV_temp.inp")
            wntr.network.write_inpfile(best_network, prv_temp)
            
            # Rename links to descriptive (A-B)
            from modules.helpers import rename_inp_links
            new_inp = tmp_path.replace(".inp", "_TriplePRV.inp")
            if rename_inp_links(prv_temp, new_inp):
                if os.path.exists(prv_temp): os.remove(prv_temp)
            else:
                new_inp = prv_temp
            
            combo_names = [f"PRV_{p}" for p in best_combo] if best_combo else ["Updated Existing PRVs"]
            
            output["prv_results"] = {
                "best_combo": combo_names,
                 "best_score": best_score,
                 "df_compare": pd.DataFrame(compare),
                 "best_network": best_network,
                 "best_result": best_result,
                 "inp_path": new_inp,
                 "score_details": {
                     "safe_nodes": best_aman,
                     "high_pressure_nodes": best_high,
                     "low_pressure_nodes": best_low
                 }
            }
    
    return output
