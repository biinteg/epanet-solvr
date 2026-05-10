# pyrefly: ignore [missing-import]
from epyt import epanet
# pyrefly: ignore [missing-import]
import networkx as nx
# pyrefly: ignore [missing-import]
import pandas as pd
import os

def run_hardy_cross(inp_path):
    """
    Runs Hardy Cross iteration and returns result data for rendering.
    Uses epyt for network parsing (wntr fallback).
    """
    d = None
    try:
        d = epanet(inp_path)
    except Exception as e:
        raise Exception(f"Gagal membaca file .inp dengan epyt: {e}")

    try:
        # Use wntr for reliable topology mapping
        # pyrefly: ignore [missing-import]
        import wntr
        wn_topo = wntr.network.WaterNetworkModel(inp_path)
        
        # Build Graph
        G = nx.MultiGraph()
        link_ids = d.getLinkNameID()
        node_ids = d.getNodeNameID()
        
        # Link properties
        diameters = d.getLinkDiameter()
        lengths = d.getLinkLength()
        roughness = d.getLinkRoughness()

        # Build a mapping of link name -> (start_node, end_node) using wntr
        link_nodes_map = {}
        for l_name in link_ids:
            link = wn_topo.get_link(l_name)
            u_name = link.start_node_name
            v_name = link.end_node_name
            link_nodes_map[l_name] = (u_name, v_name)
            
            # Add to graph if physical pipe
            l_idx = link_ids.index(l_name)
            if diameters[l_idx] > 0 and lengths[l_idx] > 0:
                G.add_edge(u_name, v_name, key=l_name)

        reservoir_names = d.getNodeReservoirNameID()
        tank_names = d.getNodeTankNameID()
        junction_names = d.getNodeJunctionNameID()
        
        source_node = reservoir_names[0] if reservoir_names else tank_names[0] if tank_names else None
        if not source_node:
            raise Exception("Jaringan harus memiliki minimal 1 Reservoir atau Tangki.")

        # Demands
        all_node_names = d.getNodeNameID()
        base_demands = d.getNodeBaseDemands() # returns list of lists or similar depending on patterns
        # For simplicity in unit tests, we take the first demand value if it's a list
        demands = {}
        for i, n_name in enumerate(all_node_names):
            val = base_demands[i]
            if isinstance(val, list):
                demands[n_name] = val[0] if val else 0.0
            else:
                demands[n_name] = val
        
        for r_name in reservoir_names + tank_names: 
            demands[r_name] = 0.0
        
        total_d = sum(demands.values())
        demands[source_node] = -total_d

        # Spanning Tree
        bfs_edges = list(nx.bfs_edges(G, source_node))
        tree_pipes = []; T_undirected = nx.Graph(); T_undirected.add_node(source_node)
        parent_map = {}
        for u, v in bfs_edges:
            T_undirected.add_edge(u, v); parent_map[v] = u
            pipe_name = list(G[u][v].keys())[0]; tree_pipes.append(pipe_name)

        # Initial Flows
        initial_flows = {p: 0.0 for p in link_ids}
        current_demands = demands.copy()
        nodes_reverse = list(reversed(list(nx.bfs_tree(G, source_node).nodes())))
        for node in nodes_reverse:
            if node == source_node: continue
            parent = parent_map[node]
            # Find the pipe connecting parent and node
            pipe_name = list(G[parent][node].keys())[0]
            
            # Check orientation using wntr mapping
            start_node_name, _ = link_nodes_map[pipe_name]
            
            required_flow = current_demands[node]
            if start_node_name == parent: 
                initial_flows[pipe_name] = required_flow
            else: 
                initial_flows[pipe_name] = -required_flow
            current_demands[parent] += required_flow

        # Loops
        chords = set([p for i, p in enumerate(link_ids) if diameters[i] > 0]) - set(tree_pipes)
        loops = []
        for chord_name in chords:
            u, v = link_nodes_map[chord_name]
            try: path_nodes = nx.shortest_path(T_undirected, v, u)
            except: continue
            loop_pipes = [(chord_name, 1)]
            for i in range(len(path_nodes)-1):
                curr_n = path_nodes[i]; next_n = path_nodes[i+1]
                for p_name in G[curr_n][next_n].keys():
                    if p_name in tree_pipes:
                        # Check orientation using wntr mapping
                        st_name, et_name = link_nodes_map[p_name]
                        loop_pipes.append((p_name, 1 if st_name == curr_n and et_name == next_n else -1))
                        break
            loops.append(loop_pipes)

        # Hardy Cross Iteration
        max_iter = 100; tolerance = 1e-5; flows = initial_flows.copy(); history = []
        converged = False; final_iter = 0

        for iteration in range(max_iter):
            max_dq = 0
            for loop_idx, loop in enumerate(loops):
                sum_hf = 0; sum_hf_over_q = 0
                for p_name, orient in loop:
                    p_idx = link_ids.index(p_name)
                    Q = flows[p_name]
                    L = lengths[p_idx]; D = diameters[p_idx]; C = roughness[p_idx]
                    if D == 0 or C == 0: continue
                    R = 10.67 * L / ((C**1.852) * (D**4.87))
                    if abs(Q) < 1e-12: hf = 0; hf_over_q = 0
                    else: hf = R * Q * (abs(Q)**0.852); hf_over_q = abs(hf / Q)
                    sum_hf += hf * orient; sum_hf_over_q += hf_over_q
                dq = - sum_hf / (1.852 * sum_hf_over_q) if sum_hf_over_q != 0 else 0
                for p_name, orient in loop: flows[p_name] += dq * orient
                max_dq = max(max_dq, abs(dq))
                history.append({"Iterasi": iteration + 1, "Loop": f"Loop {loop_idx + 1}", "ΔQ (L/s)": dq * 1000})
            if max_dq < tolerance: converged = True; final_iter = iteration + 1; break

        final_results = []
        for i, p_name in enumerate(link_ids):
            if diameters[i] > 0:
                u, v = link_nodes_map[p_name]
                final_results.append({
                    "Pipa ID": f"{p_name} ({u}-{v})",
                    "Debit Awal (L/s)": initial_flows[p_name] * 1000,
                    "Debit Akhir (L/s)": flows[p_name] * 1000
                })
        
        return {
            "type": "hardy_cross",
            "history_df": pd.DataFrame(history),
            "final_df": pd.DataFrame(final_results),
            "converged": converged,
            "iterations": final_iter,
            "flows": flows,
            "loops_found": len(loops)
        }
    finally:
        if d:
            d.unload()

