# pyrefly: ignore [missing-import]
import streamlit as st
# pyrefly: ignore [missing-import]
from epyt import epanet
# pyrefly: ignore [missing-import]
import pandas as pd
import os
# pyrefly: ignore [missing-import]
import wntr
from modules.helpers import (
    MAX_HEADLOSS_M_PER_KM,
    MAX_VELOCITY_MS,
    MIN_VELOCITY_MS,
    MIN_PRESSURE_M,
    warnai_status_solver,
)

def run_auto_solver(tmp_path):
    """
    Runs the auto-solver and returns a dictionary with the results dataframe,
    summary metrics, and the path to the optimized INP file.
    """
    d = None
    try:
        # Use wntr for reliable topology mapping
        wn = wntr.network.WaterNetworkModel(tmp_path)
        pipe_names_map = {}
        for p_name in wn.pipe_name_list:
            pipe = wn.get_link(p_name)
            pipe_names_map[p_name] = f"Pipa {pipe.start_node_name} - {pipe.end_node_name}"
            
        d = epanet(tmp_path)
        link_ids = d.getLinkNameID()
        diameter_awal = d.getLinkDiameter()

        standar_pipa = [50, 75, 100, 150, 200, 250, 300, 400, 500, 600, 800]

        # Iterasi optimasi (Ditingkatkan ke 10 iterasi)
        for iterasi in range(10):
            d.openHydraulicAnalysis()
            d.runHydraulicAnalysis()
            d.closeHydraulicAnalysis()

            velocity = d.getLinkVelocity()
            headloss = d.getLinkHeadloss()
            pressures = d.getNodePressure()
            node_ids = d.getNodeNameID()

            # Mapping node_id to pressure
            node_p_map = {node_ids[j]: pressures[j] for j in range(len(node_ids))}

            for i in range(len(link_ids)):
                link_info = wn.get_link(link_ids[i])
                length_km = link_info.length / 1000.0 if link_info.length > 0 else 1.0
                
                v = abs(velocity[i])
                # Convert total headloss to headloss per km (m/km)
                h_grad = abs(headloss[i]) / length_km
                
                d_now = d.getLinkDiameter(i + 1)
                d_new = d_now

                # Logic dasar: Atur diameter berdasarkan velocity dan headloss gradient
                if 0.001 < v < MIN_VELOCITY_MS:
                    kandidat = [x for x in standar_pipa if x < d_now]
                    if kandidat:
                        d_new = max(kandidat)
                elif v > MAX_VELOCITY_MS or h_grad > MAX_HEADLOSS_M_PER_KM:
                    kandidat = [x for x in standar_pipa if x > d_now]
                    if kandidat:
                        d_new = min(kandidat)

                # TAMBAHAN: Proteksi Tekanan
                # Jika diameter diperkecil, cek apakah tekanan di node hilir masih aman
                if d_new < d_now:
                    # Ambil node end (hilir biasanya)
                    end_node = link_info.end_node_name
                    p_hilir = node_p_map.get(end_node, 100)
                    
                    if p_hilir < MIN_PRESSURE_M: # Gunakan batas minimum standar (10m)
                        d_new = d_now # Batal diperkecil demi menjaga tekanan
                
                if d_new != d_now:
                    d.setLinkDiameter(i + 1, d_new)

        # Run final
        d.openHydraulicAnalysis()
        d.runHydraulicAnalysis()
        d.closeHydraulicAnalysis()

        final_velocity = d.getLinkVelocity()
        final_headloss = d.getLinkHeadloss()
        final_pressures = d.getNodePressure()
        final_node_ids = d.getNodeNameID()
        final_node_p_map = {final_node_ids[j]: final_pressures[j] for j in range(len(final_node_ids))}

        hasil = []
        berubah = 0
        patuh = 0

        for i in range(len(link_ids)):
            link_info = wn.get_link(link_ids[i])
            length_km = link_info.length / 1000.0 if link_info.length > 0 else 1.0

            awal = diameter_awal[i]
            akhir = d.getLinkDiameter(i + 1)
            v = abs(final_velocity[i])
            h_grad = abs(final_headloss[i]) / length_km
            
            sesuai_permen = MIN_VELOCITY_MS <= v <= MAX_VELOCITY_MS and h_grad <= MAX_HEADLOSS_M_PER_KM

            if akhir > awal:
                status = "Diperbesar"
            elif akhir < awal:
                status = "Diperkecil"
            else:
                status = "Tetap"

            if awal != akhir:
                berubah += 1
            if sesuai_permen:
                patuh += 1

            # Use the mapping created with wntr
            label_pipa = pipe_names_map.get(link_ids[i], f"Pipa {link_ids[i]}")

            # Ambil tekanan di node hilir untuk ditampilkan
            p_hilir_val = final_node_p_map.get(link_info.end_node_name, 0)

            hasil.append({
                "ID": link_ids[i],
                "Nama Pipa": label_pipa,
                "Diameter Awal": f"{awal:.0f} mm",
                "Diameter Baru": f"{akhir:.0f} mm",
                "Velocity": f"{v:.3f} m/s",
                "Headloss": f"{h_grad:.3f} m/km",
                "Pressure": f"{p_hilir_val:.1f} m",
                "Status": status,
                "Compliance": "Aman" if sesuai_permen else "Tidak Aman"
            })

        df = pd.DataFrame(hasil)
        
        # Save optimized INP
        final_temp = tmp_path.replace(".inp", "_optimized.inp")
        d.saveInputFile(final_temp)
        
        # Rename links to descriptive (A-B)
        # pyrefly: ignore [missing-import]
        from modules.helpers import rename_inp_links
        new_inp = tmp_path.replace(".inp", "_final.inp")
        if rename_inp_links(final_temp, new_inp):
            if os.path.exists(final_temp): os.remove(final_temp)
        else:
            new_inp = final_temp # Fallback

        # Return results to view
        return {
            "type": "auto_solver",
            "df": df,
            "metrics": {
                "total": len(link_ids),
                "changed": berubah,
                "compliant": patuh
            },
            "inp_file_path": new_inp
        }

    finally:
        if d:
            d.unload()
