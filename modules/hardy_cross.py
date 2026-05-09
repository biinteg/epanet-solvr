# pyrefly: ignore [missing-import]
import wntr
# pyrefly: ignore [missing-import]
import networkx as nx
# pyrefly: ignore [missing-import]
import pandas as pd
import os

def run_hardy_cross(inp_path):
    """
    Runs Hardy Cross iteration and returns result data for rendering.
    """
    try:
        wn = wntr.network.WaterNetworkModel(inp_path)
    except Exception as e:
        raise Exception(f"Gagal membaca file .inp: {e}")

    # Build Graph
    G = nx.MultiGraph()
    for pipe_name in wn.pipe_name_list:
        pipe = wn.get_link(pipe_name)
        if pipe.diameter > 0 and pipe.length > 0:
            G.add_edge(pipe.start_node_name, pipe.end_node_name, key=pipe_name)

    source_node = wn.reservoir_name_list[0] if wn.reservoir_name_list else wn.tank_name_list[0] if wn.tank_name_list else None
    if not source_node:
        raise Exception("Jaringan harus memiliki minimal 1 Reservoir atau Tangki.")

    demands = {}
    for j_name in wn.junction_name_list:
        j = wn.get_node(j_name)
        try: d = j.demand_timeseries_list[0].base_value
        except: d = 0.0
        demands[j_name] = d
    for r_name in wn.reservoir_name_list + wn.tank_name_list: demands[r_name] = 0.0
    
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
    initial_flows = {p: 0.0 for p in wn.pipe_name_list}
    current_demands = demands.copy()
    nodes_reverse = list(reversed(list(nx.bfs_tree(G, source_node).nodes())))
    for node in nodes_reverse:
        if node == source_node: continue
        parent = parent_map[node]
        pipe_name = list(G[parent][node].keys())[0]
        pipe = wn.get_link(pipe_name)
        required_flow = current_demands[node]
        if pipe.start_node_name == parent and pipe.end_node_name == node: initial_flows[pipe_name] = required_flow
        else: initial_flows[pipe_name] = -required_flow
        current_demands[parent] += required_flow

    # Loops
    chords = set([p for p in wn.pipe_name_list if wn.get_link(p).diameter > 0]) - set(tree_pipes)
    loops = []
    for chord_name in chords:
        chord = wn.get_link(chord_name); u = chord.start_node_name; v = chord.end_node_name
        try: path_nodes = nx.shortest_path(T_undirected, v, u)
        except: continue
        loop_pipes = [(chord_name, 1)]
        for i in range(len(path_nodes)-1):
            curr_n = path_nodes[i]; next_n = path_nodes[i+1]
            for p_name in G[curr_n][next_n].keys():
                if p_name in tree_pipes:
                    p = wn.get_link(p_name)
                    loop_pipes.append((p_name, 1 if p.start_node_name == curr_n and p.end_node_name == next_n else -1))
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
                p = wn.get_link(p_name); Q = flows[p_name]
                L = p.length; D = p.diameter; C = p.roughness
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
    for p_name in wn.pipe_name_list:
        if wn.get_link(p_name).diameter > 0:
            p = wn.get_link(p_name)
            final_results.append({
                "Pipa ID": f"{p_name} ({p.start_node_name}-{p.end_node_name})",
                "Debit Awal (L/s)": initial_flows[p_name] * 1000,
                "Debit Akhir (L/s)": flows[p_name] * 1000
            })
    
    return {
        "type": "hardy_cross",
        "history_df": pd.DataFrame(history),
        "final_df": pd.DataFrame(final_results),
        "converged": converged,
        "iterations": final_iter,
        "wn": wn,
        "flows": flows,
        "loops_found": len(loops)
    }
