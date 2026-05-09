import wntr
import networkx as nx
import pandas as pd
import streamlit as st
import tempfile
import os

def run_hardy_cross(inp_path):
    st.markdown("## 🔄 Analisis Jaringan dengan Metode Hardy Cross")
    st.write(
        "Metode Hardy Cross adalah metode iteratif manual untuk menghitung "
        "aliran dalam jaringan pipa tertutup (loop)."
    )

    try:
        wn = wntr.network.WaterNetworkModel(inp_path)
    except Exception as e:
        st.error(f"Gagal membaca file .inp: {e}")
        return

    # Validasi jaringan (Hardy Cross optimal untuk jaringan sederhana tanpa pompa/valve)
    if len(wn.pump_name_list) > 0 or len(wn.valve_name_list) > 0:
        st.warning(
            "⚠️ **Peringatan**: Jaringan ini mengandung Pompa atau Valve. "
            "Metode Hardy Cross murni (berdasarkan formula pipa Hazen-Williams) "
            "mungkin tidak memberikan hasil yang akurat untuk komponen non-pipa. "
            "Komponen tersebut akan diabaikan/dilewati dalam iterasi loop."
        )

    if len(wn.reservoir_name_list) == 0 and len(wn.tank_name_list) == 0:
        st.error("❌ **Error**: Jaringan harus memiliki minimal 1 Reservoir atau Tangki sebagai sumber (slack node).")
        return

    with st.spinner("Membangun model graf jaringan..."):
        # 1. Bangun MultiGraph
        G = nx.MultiGraph()
        for pipe_name in wn.pipe_name_list:
            pipe = wn.get_link(pipe_name)
            if pipe.diameter > 0 and pipe.length > 0:
                G.add_edge(pipe.start_node_name, pipe.end_node_name, key=pipe_name)

        # 2. Tentukan source node (Reservoir/Tank pertama)
        source_node = None
        if wn.reservoir_name_list:
            source_node = wn.reservoir_name_list[0]
        else:
            source_node = wn.tank_name_list[0]

        # 3. Hitung Demands
        demands = {}
        for j_name in wn.junction_name_list:
            j = wn.get_node(j_name)
            try:
                # Ambil base demand (m3/s)
                d = j.demand_timeseries_list[0].base_value
            except:
                d = 0.0
            demands[j_name] = d

        for r_name in wn.reservoir_name_list + wn.tank_name_list:
            demands[r_name] = 0.0

        total_d = sum(demands.values())
        demands[source_node] = -total_d  # Source menyuplai total demand

        # 4. Bangun Spanning Tree (BFS)
        bfs_edges = list(nx.bfs_edges(G, source_node))
        
        # Konversi edge BFS ke pipa
        tree_pipes = []
        T_undirected = nx.Graph()
        T_undirected.add_node(source_node)
        
        # Mapping untuk child -> parent (arah tree dari leaf ke root)
        parent_map = {}
        for u, v in bfs_edges:
            T_undirected.add_edge(u, v)
            # Edge dari u ke v di BFS, berarti parent dari v adalah u
            parent_map[v] = u
            
            # Cari nama pipanya
            pipe_name = list(G[u][v].keys())[0]
            tree_pipes.append(pipe_name)

        # 5. Tentukan Aliran Awal (Initial Flows) yang memenuhi kontinuitas
        initial_flows = {p: 0.0 for p in wn.pipe_name_list}
        current_demands = demands.copy()

        # Urutkan node dari leaf ke root (Post-order / reverse BFS)
        nodes_reverse = list(reversed(list(nx.bfs_tree(G, source_node).nodes())))

        for node in nodes_reverse:
            if node == source_node:
                continue
            
            parent = parent_map[node]
            pipe_name = list(G[parent][node].keys())[0]
            pipe = wn.get_link(pipe_name)
            
            required_flow = current_demands[node]
            
            if pipe.start_node_name == parent and pipe.end_node_name == node:
                initial_flows[pipe_name] = required_flow
            else:
                initial_flows[pipe_name] = -required_flow
                
            current_demands[parent] += required_flow

        # 6. Cari Fundamental Loops (Chords)
        chords = set([p for p in wn.pipe_name_list if wn.get_link(p).diameter > 0]) - set(tree_pipes)
        
        loops = []
        for chord_name in chords:
            chord = wn.get_link(chord_name)
            u = chord.start_node_name
            v = chord.end_node_name
            
            try:
                path_nodes = nx.shortest_path(T_undirected, v, u)
            except nx.NetworkXNoPath:
                continue
                
            loop_pipes = []
            loop_pipes.append((chord_name, 1))
            
            for i in range(len(path_nodes)-1):
                curr_n = path_nodes[i]
                next_n = path_nodes[i+1]
                
                # Cari pipa tree yang menghubungkan
                for p_name in G[curr_n][next_n].keys():
                    if p_name in tree_pipes:
                        p = wn.get_link(p_name)
                        if p.start_node_name == curr_n and p.end_node_name == next_n:
                            loop_pipes.append((p_name, 1))
                        else:
                            loop_pipes.append((p_name, -1))
                        break
            loops.append(loop_pipes)

    if not loops:
        st.success("✅ Jaringan merupakan sistem cabang (Branching / Tree). Tidak ada sirkuit tertutup (loop), sehingga aliran awal sudah merupakan hasil yang tepat.")
    else:
        st.info(f"🔍 Ditemukan **{len(loops)} fundamental loops** dalam jaringan. Memulai iterasi Hardy Cross...")

    # =========================================================================
    # HARDY CROSS ITERATION
    # =========================================================================
    max_iter = 100
    tolerance = 1e-5 # m3/s (~0.01 L/s)
    flows = initial_flows.copy()
    history = []

    progress_bar = st.progress(0)
    status_text = st.empty()

    converged = False
    final_iter = 0

    for iteration in range(max_iter):
        max_dq = 0
        iter_data = []
        
        for loop_idx, loop in enumerate(loops):
            sum_hf = 0
            sum_hf_over_q = 0
            
            for p_name, orient in loop:
                p = wn.get_link(p_name)
                Q = flows[p_name]
                
                L = p.length
                D = p.diameter
                C = p.roughness
                
                if D == 0 or C == 0:
                    continue
                    
                # HW Resistance R = 10.67 * L / (C^1.852 * D^4.87)
                R = 10.67 * L / ((C**1.852) * (D**4.87))
                
                if abs(Q) < 1e-12:
                    hf = 0
                    hf_over_q = 0
                else:
                    hf = R * Q * (abs(Q)**0.852)
                    hf_over_q = abs(hf / Q)
                
                hf_loop = hf * orient
                
                sum_hf += hf_loop
                sum_hf_over_q += hf_over_q
                
            if sum_hf_over_q == 0:
                dq = 0
            else:
                dq = - sum_hf / (1.852 * sum_hf_over_q)
                
            for p_name, orient in loop:
                flows[p_name] += dq * orient
                
            max_dq = max(max_dq, abs(dq))
            iter_data.append({
                "Iterasi": iteration + 1,
                "Loop": f"Loop {loop_idx + 1}",
                "ΔQ (L/s)": dq * 1000
            })
            
        history.extend(iter_data)
        
        progress_bar.progress((iteration + 1) / max_iter)
        status_text.text(f"Iterasi {iteration + 1}... Max ΔQ = {max_dq*1000:.4f} L/s")
        
        if max_dq < tolerance:
            converged = True
            final_iter = iteration + 1
            break

    progress_bar.empty()
    status_text.empty()

    if loops:
        if converged:
            st.success(f"✅ **Konvergen!** Solusi ditemukan pada iterasi ke-{final_iter}.")
        else:
            st.warning(f"⚠️ **Batas Maksimum Iterasi Tercapai!** Algoritma dihentikan pada iterasi {max_iter} namun nilai ΔQ masih di atas toleransi.")

    # =========================================================================
    # DISPLAY RESULTS
    # =========================================================================
    col1, col2 = st.columns(2)

    # DataFrame Sejarah Iterasi
    if history:
        with col1:
            st.markdown("### 📈 Ringkasan Iterasi (Koreksi ΔQ)")
            df_history = pd.DataFrame(history)
            st.dataframe(df_history, height=350, use_container_width=True)

    # DataFrame Hasil Akhir
    with col2:
        st.markdown("### 🚰 Hasil Aliran Akhir")
        final_results = []
        for p_name in wn.pipe_name_list:
            if wn.get_link(p_name).diameter > 0:
                final_results.append({
                    "Pipa ID": p_name,
                    "Debit Awal (L/s)": initial_flows[p_name] * 1000,
                    "Debit Akhir (L/s)": flows[p_name] * 1000
                })
        
        df_final = pd.DataFrame(final_results)
        # Format ke 2 desimal
        st.dataframe(
            df_final.style.format({
                "Debit Awal (L/s)": "{:.2f}", 
                "Debit Akhir (L/s)": "{:.2f}"
            }), 
            height=350, 
            use_container_width=True
        )

    # Unduh Hasil
    csv = df_final.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Unduh Hasil Hardy Cross (CSV)",
        data=csv,
        file_name="hasil_hardy_cross.csv",
        mime="text/csv",
    )
