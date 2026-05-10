# pyrefly: ignore [missing-import]
import pandas as pd
# pyrefly: ignore [missing-import]
import matplotlib.pyplot as plt
# pyrefly: ignore [missing-import]
import numpy as np
# pyrefly: ignore [missing-import]
import wntr
# pyrefly: ignore [missing-import]
import streamlit as st
# pyrefly: ignore [missing-import]
import plotly.graph_objects as go
# pyrefly: ignore [missing-import]
import plotly.express as px

MIN_PRESSURE_M = 10
MAX_PRESSURE_M = 80
MIN_VELOCITY_MS = 0.3
MAX_VELOCITY_MS = 2.5
MAX_HEADLOSS_M_PER_KM = 10

# =====================================================
# FUNGSI WARNA
# =====================================================

def warnai_status_tekanan(val):
    if val == "Aman":
        return "color: limegreen; font-weight: bold;"
    else:
        return "color: red; font-weight: bold;"

def warnai_status_solver(val):
    if val == "Diperbesar":
        return "color: limegreen; font-weight: bold;"
    elif val == "Diperkecil":
        return "color: orange; font-weight: bold;"
    else:
        return "color: cyan; font-weight: bold;"

def tampilkan_network(wn, tekanan_dict=None, judul="Visualisasi Jaringan"):
    fig, ax = plt.subplots(figsize=(14, 10))
    
    # Plot network dasar
    wntr.graphics.plot_network(wn, title=judul, ax=ax, node_size=20)
    
    # Tambahkan scatter plot + label untuk node dengan warna berdasarkan tekanan
    if tekanan_dict is not None:
        node_xy = []
        node_colors = []
        node_labels = []
        
        for node_name in wn.junction_name_list:
            node = wn.get_node(node_name)
            x, y = node.coordinates
            node_xy.append([x, y])
            
            p = tekanan_dict[node_name]
            # Pengaman angka absurd
            if pd.isna(p) or p < -100:
                p = 0
            
            if p < MIN_PRESSURE_M:
                node_colors.append("red")
                color_text = 'white'
            elif p > MAX_PRESSURE_M:
                node_colors.append("orange")
                color_text = 'black'
            else:
                node_colors.append("limegreen")
                color_text = 'black'
            
            # Format label: nama node + tekanan (1 desimal)
            label = f"{node_name}\n{p:.1f}"
            node_labels.append((x, y, label, color_text))
        
        if node_xy:
            node_xy = np.array(node_xy)
            # Scatter plot dengan ukuran lebih besar
            scatter = ax.scatter(node_xy[:, 0], node_xy[:, 1], 
                                c=node_colors, s=200, zorder=10, 
                                edgecolors='black', linewidth=2,
                                alpha=0.9)
            
            # TAMBAHAN: Label angka tekanan pada setiap node
            for x, y, label, color_text in node_labels:
                ax.annotate(label, (x, y), 
                           xytext=(0, 15), textcoords='offset points',
                           ha='center', va='bottom', fontsize=9,
                           fontweight='bold', color=color_text,
                           bbox=dict(boxstyle="round,pad=0.3", 
                                   facecolor='white', alpha=0.8,
                                   edgecolor=color_text, linewidth=1),
                           zorder=11)
    
    # Colorbar atau legend
    if tekanan_dict is not None:
        # pyrefly: ignore [missing-import]
        from matplotlib.lines import Line2D
        legend_elements = [
            Line2D([0], [0], marker='o', color='w', markerfacecolor='limegreen',
                   markersize=12, label=f'Aman ({MIN_PRESSURE_M}-{MAX_PRESSURE_M} m)', markeredgecolor='black'),
            Line2D([0], [0], marker='o', color='w', markerfacecolor='orange',
                   markersize=12, label=f'Tinggi (>{MAX_PRESSURE_M} m)', markeredgecolor='black'),
            Line2D([0], [0], marker='o', color='w', markerfacecolor='red',
                   markersize=12, label=f'Rendah (<{MIN_PRESSURE_M} m)', markeredgecolor='black')
        ]
        ax.legend(handles=legend_elements, loc='upper right', frameon=True, fontsize=10)
    
    # Styling tambahan
    ax.set_xlabel("X (m)", fontsize=12, fontweight='bold')
    ax.set_ylabel("Y (m)", fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.set_facecolor('#fdfdfd')
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

def tampilkan_network_plotly(wn, tekanan_dict=None, judul="Interactive Network Visualization"):
    """Menampilkan jaringan menggunakan Plotly agar interaktif (bisa zoom/hover)"""
    
    edge_x = []
    edge_y = []
    for edge in wn.links():
        start_node = wn.get_node(edge[1].start_node_name)
        end_node = wn.get_node(edge[1].end_node_name)
        x0, y0 = start_node.coordinates
        x1, y1 = end_node.coordinates
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=1, color='#888'),
        hoverinfo='none',
        mode='lines')

    node_x = []
    node_y = []
    node_text = []
    node_color = []
    
    for node_name in wn.node_name_list:
        node = wn.get_node(node_name)
        x, y = node.coordinates
        node_x.append(x)
        node_y.append(y)
        
    node_pressures_numeric = []
    for node_name in wn.node_name_list:
        p = tekanan_dict.get(node_name, 0) if tekanan_dict is not None else 0
        if pd.isna(p): p = 0
        node_pressures_numeric.append(p)
        
        info = f"Node: {node_name}<br>Pressure: {p:.2f} m"
        node_text.append(info)

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers',
        hoverinfo='text',
        text=node_text,
        marker=dict(
            showscale=True,
            colorscale='RdYlGn',
            reversescale=False,
            color=node_pressures_numeric,
            size=14,
            colorbar=dict(
                thickness=15,
                title='Pressure (m)',
                xanchor='left',
                titleside='right'
            ),
            line_width=2,
            line_color='white'))

    fig = go.Figure(data=[edge_trace, node_trace],
                 layout=go.Layout(
                    title=judul,
                    titlefont_size=20,
                    showlegend=False,
                    hovermode='closest',
                    margin=dict(b=20,l=5,r=5,t=60),
                    xaxis=dict(showgrid=True, zeroline=False, showticklabels=False, gridcolor='#eee'),
                    yaxis=dict(showgrid=True, zeroline=False, showticklabels=False, gridcolor='#eee'),
                    template='plotly_white',
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)'
                ))
    
    st.plotly_chart(fig, use_container_width=True)

def tampilkan_skema_jaringan(wn, judul="Skema Jaringan"):
    """
    Menampilkan skema jaringan dengan tampilan bersih:
    - Junction: Titik Biru
    - Reservoir: Titik Merah
    - Pipa: Garis Biru Tipis
    - Tanpa axes/grid (Style Premium)
    """
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # 1. Plot Pipes (Default grey)
    wntr.graphics.plot_network(wn, ax=ax, node_size=0, link_width=1.2)
    
    # 2. Plot Junctions (Clean blue dots)
    junction_coords = []
    for name in wn.junction_name_list:
        junction_coords.append(wn.get_node(name).coordinates)
    if junction_coords:
        junction_coords = np.array(junction_coords)
        ax.scatter(junction_coords[:,0], junction_coords[:,1], c='#3498db', s=45, label='JUNCTION', zorder=5, edgecolors='white', linewidth=1)
        
    # 3. Plot Reservoirs (Bold red squares)
    res_coords = []
    for name in wn.reservoir_name_list:
        res_coords.append(wn.get_node(name).coordinates)
    if res_coords:
        res_coords = np.array(res_coords)
        ax.scatter(res_coords[:,0], res_coords[:,1], c='#e74c3c', s=100, marker='s', label='RESERVOIR', zorder=6, edgecolors='black', linewidth=1.5)
        
    # 4. Plot Tanks (Green cylinders/hexagons)
    tank_coords = []
    for name in wn.tank_name_list:
        tank_coords.append(wn.get_node(name).coordinates)
    if tank_coords:
        tank_coords = np.array(tank_coords)
        ax.scatter(tank_coords[:,0], tank_coords[:,1], c='#2ecc71', s=120, marker='h', label='TANK', zorder=6, edgecolors='black', linewidth=1.5)

    # 5. Plot Valves (Orange triangles)
    valve_coords = []
    for name in wn.valve_name_list:
        valve = wn.get_link(name)
        # Use midpoint or start node
        start_node = wn.get_node(valve.start_node_name)
        end_node = wn.get_node(valve.end_node_name)
        mid_x = (start_node.coordinates[0] + end_node.coordinates[0]) / 2
        mid_y = (start_node.coordinates[1] + end_node.coordinates[1]) / 2
        valve_coords.append([mid_x, mid_y])
    if valve_coords:
        valve_coords = np.array(valve_coords)
        ax.scatter(valve_coords[:,0], valve_coords[:,1], c='#f39c12', s=80, marker='D', label='VALVE/PRV', zorder=7, edgecolors='black', linewidth=1)

    # Styling
    ax.set_title(judul, fontsize=18, pad=25, fontweight='bold', color='#2c3e50')
    ax.legend(loc='lower left', frameon=True, fontsize=10, shadow=True, borderpad=1)
    ax.set_axis_off() 
    
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

def rename_inp_links(inp_path, out_path):
    """
    Mengubah ID pipa dari p1, p2 menjadi format deskriptif (A-B) di dalam file .inp.
    Menggunakan wntr untuk mapping dan manipulasi teks yang aman.
    """
    try:
        wn = wntr.network.WaterNetworkModel(inp_path)
        mapping = {}
        
        # Buat mapping ID lama -> ID baru (Format: Node1_Node2)
        for name, link in wn.links():
            # Hindari karakter terlarang di EPANET
            s = str(link.start_node).replace(" ", "_").replace(";", "")
            e = str(link.end_node).replace(" ", "_").replace(";", "")
            new_id = f"{s}-{e}"
            # Jika ID terlalu panjang, potong (limit EPANET ID biasanya 31-255 tergantung versi)
            if len(new_id) > 31:
                new_id = new_id[:31]
            mapping[name] = new_id

        with open(inp_path, 'r') as f:
            lines = f.readlines()

        new_lines = []
        current_section = ""
        
        # Daftar section yang mengandung ID Link
        link_sections = ["[PIPES]", "[PUMPS]", "[VALVES]", "[STATUS]", "[CONTROLS]", "[RULES]", "[REPORT]", "[TAGS]", "[VERTICES]"]

        for line in lines:
            stripped = line.strip()
            if stripped.startswith("[") and stripped.endswith("]"):
                current_section = stripped.upper()
                new_lines.append(line)
                continue
            
            # Abaikan komentar atau baris kosong
            if not stripped or stripped.startswith(";"):
                new_lines.append(line)
                continue

            # Proses penggantian ID jika berada di section yang relevan
            if current_section in link_sections:
                parts = line.split()
                if parts and parts[0] in mapping:
                    old_id = parts[0]
                    new_id = mapping[old_id]
                    # Ganti hanya kata pertama (ID) agar kolom lain tetap terjaga
                    line = line.replace(old_id, new_id, 1)
            
            new_lines.append(line)

        with open(out_path, 'w') as f:
            f.writelines(new_lines)
        return True
    except Exception as e:
        print(f"Error renaming INP: {e}")
        return False
