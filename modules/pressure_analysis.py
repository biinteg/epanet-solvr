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
        kandidat_pipa = [p for p in wn.pipe_name_list if wn.get_link(p).diameter > 0.15]
        if len(kandidat_pipa) >= 3:
            combos = list(combinations(kandidat_pipa, 3))
            best_score = -1; best_combo = None; best_result = {}; best_network = None

            for combo in combos:
                try:
                    wn_test = wntr.network.WaterNetworkModel(tmp_path)
                    for pipe_name in combo:
                        pipe = wn_test.get_link(pipe_name)
                        wn_test.remove_link(pipe_name)
                        wn_test.add_valve(f"PRV_{pipe_name}", pipe.start_node_name, pipe.end_node_name, 
                                        diameter=pipe.diameter, valve_type="PRV", initial_setting=target_prv)
                    sim_test = wntr.sim.EpanetSimulator(wn_test)
                    res = sim_test.run_sim()
                    tekanan = res.node["pressure"].iloc[0]
                    if any(pd.isna(tekanan[n]) or tekanan[n] < -100 for n in wn_test.junction_name_list): continue
                    aman = sum(1 for n in wn_test.junction_name_list if MIN_PRESSURE_M <= tekanan[n] <= MAX_PRESSURE_M)
                    if aman > best_score:
                        best_score = aman; best_combo = combo; best_result = tekanan; best_network = wn_test
                except: continue

            if best_combo:
                compare = []
                for node in wn.junction_name_list:
                    new_p = best_result[node]
                    p_tampil = new_p if (pd.notna(new_p) and new_p > -100) else 0
                    status = "Terlalu Rendah" if p_tampil < MIN_PRESSURE_M else "Bahaya (Terlalu Tinggi)" if p_tampil > MAX_PRESSURE_M else "Aman"
                    compare.append({"Node": node, "Tekanan Lama": round(tekanan_awal[node], 2), "Tekanan Baru": round(p_tampil, 2), "Status": status})
                
                prv_temp = tmp_path.replace(".inp", "_PRV_temp.inp")
                wntr.network.write_inpfile(best_network, prv_temp)
                
                # Rename links to descriptive (A-B)
                # pyrefly: ignore [missing-import]
                from modules.helpers import rename_inp_links
                new_inp = tmp_path.replace(".inp", "_TriplePRV.inp")
                if rename_inp_links(prv_temp, new_inp):
                    if os.path.exists(prv_temp): os.remove(prv_temp)
                else:
                    new_inp = prv_temp
                
                output["prv_results"] = {
                    "best_combo": best_combo,
                    "best_score": best_score,
                    "df_compare": pd.DataFrame(compare),
                    "best_network": best_network,
                    "best_result": best_result,
                    "inp_path": new_inp
                }
    
    return output
