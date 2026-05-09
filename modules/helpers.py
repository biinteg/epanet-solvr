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
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

def tampilkan_skema_jaringan(wn, judul="Skema Jaringan"):
    """
    Menampilkan skema jaringan dengan tampilan bersih:
    - Junction: Titik Biru
    - Reservoir: Titik Merah
    - Pipa: Garis Biru Tipis
    - Tanpa axes/grid (Style Premium)
    """
    fig, ax = plt.subplots(figsize=(12, 8))
    
    wntr.graphics.plot_network(wn, ax=ax, node_size=0, link_width=1.5)
    
    # 2. Plot Junctions (Blue dots)
    junction_coords = []
    for name in wn.junction_name_list:
        junction_coords.append(wn.get_node(name).coordinates)
    if junction_coords:
        junction_coords = np.array(junction_coords)
        ax.scatter(junction_coords[:,0], junction_coords[:,1], c='blue', s=40, label='JUNCTION', zorder=5)
        
    # 3. Plot Reservoirs (Red dots)
    res_coords = []
    for name in wn.reservoir_name_list:
        res_coords.append(wn.get_node(name).coordinates)
    if res_coords:
        res_coords = np.array(res_coords)
        ax.scatter(res_coords[:,0], res_coords[:,1], c='red', s=60, label='RESERVOIR', zorder=6)
        
    # 4. Plot Tanks (Green dots if any)
    tank_coords = []
    for name in wn.tank_name_list:
        tank_coords.append(wn.get_node(name).coordinates)
    if tank_coords:
        tank_coords = np.array(tank_coords)
        ax.scatter(tank_coords[:,0], tank_coords[:,1], c='forestgreen', s=60, label='TANK', zorder=6)

    # Styling
    ax.set_title(judul, fontsize=16, pad=20, fontweight='bold')
    ax.legend(loc='upper right', frameon=False, fontsize=10)
    ax.set_axis_off() # Menghilangkan axes agar bersih seperti di gambar
    
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)
