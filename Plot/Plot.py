import os
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib.cm import ScalarMappable
from matplotlib.lines import Line2D
from ParameterConfig import *
import ParameterConfig
from Node import *
from Gateway import *

def Training_Chart(Method_Config):
    subfolder_name = f"{nrNodes}_nodes_{radius}_m"
    Method_Config.result_folder_path = os.path.join(Method_Config.result_folder_path, subfolder_name)
    
    '''Network Energy Efficiency'''
    plt.figure()
    x = range(1,Method_Config.num_episode+1)
    plt.plot(x, Method_Config.NetworkEnergyEfficiency, label='NetworkEnergyEfficiency', color='blue')

    plt.title('Network Energy Efficiency changes with increasing episode')
    plt.xlabel('Episode')
    plt.ylabel('Energy Efficiency/(bits/mJ)')
    plt.legend()

    fig1_name = 'NetworkEnergyEfficiency_plot.png'
    plt.savefig(os.path.join(Method_Config.result_folder_path, fig1_name))

    '''Network PDR'''
    plt.figure()
    plt.plot(x, Method_Config.Network_PDR, '-', color='b')
    plt.title('Network PDR changes with increasing episode')
    plt.xlabel('Episode')
    plt.ylabel('Network PDR')

    fig2_name = 'Network_PDR_plot.png'
    plt.savefig(os.path.join(Method_Config.result_folder_path, fig2_name))

def sf_distribution(folder_path):
    # SF_COLORS = {
    #     7: 'lightgray',          # Very light, near-white
    #     8: 'khaki',              # Yellowish
    #     9: 'mediumaquamarine',   # Aqua-green
    #     10: 'lightskyblue',      # Light blue
    #     11: 'cornflowerblue',    # Medium blue
    #     12: 'darkorange',        # Deep orange
    # }
    SF_COLORS = {
        7: '#1f77b4',  # 蓝
        8: '#ff7f0e',  # 橙
        9: '#2ca02c',  # 绿
        10: '#8c564b', # 棕
        11: '#9467bd', # 紫
        12: '#d62728', # 红
    }

    GATEWAY_COLOR = 'black'
    GATEWAY_MARKER = '^'

    # --- Plotting ---
    fig, ax = plt.subplots(figsize=(9, 9)) # Make it square for equal aspect ratio

    # Gateway is at (0,0) on the plot, units are meters.
    
    ax.scatter(ParameterConfig.GW.x, ParameterConfig.GW.y,
            marker=GATEWAY_MARKER, color=GATEWAY_COLOR, s=350, zorder=10, label="Gateway")

    # Plot Nodes
    for node in nodes:
        color = SF_COLORS.get(node.sf, 'grey') # Default to grey if SF not in map

        ax.scatter(node.x, node.y, color=color, s=150, alpha=0.8)

    # --- Customize Plot (axes, labels, legend) ---
    ax.set_aspect('equal', adjustable='box') # Both axes in meters, 'equal' is appropriate

    # ax.set_title("LoRa Network Topology - SF Distribution", fontsize=14, pad=30)

    num_ticks = 5 # Number of ticks on each side of zero, plus zero (or adjust as needed)

    # X-axis (m)
    x_tick_positions = np.linspace(-radius, radius, num_ticks)
    ax.set_xlabel("Distance (m)", fontsize=24)
    ax.set_xticks(x_tick_positions)
    ax.set_xticklabels([f"{tick:.0f}" for tick in x_tick_positions]) # Integers for meters
    ax.set_xlim(-radius * 1.1, radius * 1.1) # Add some padding

    # Y-axis (m)
    y_tick_positions = np.linspace(-radius, radius, num_ticks)
    ax.set_ylabel("Distance (m)", fontsize=24)
    ax.set_yticks(y_tick_positions)
    ax.set_yticklabels([f"{tick:.0f}" for tick in y_tick_positions]) # Integers for meters
    ax.set_ylim(-radius * 1.1, radius * 1.1) # Add some padding

    ax.tick_params(axis='x', labelsize=22)  # 设置 x 轴刻度字体大小为 12
    ax.tick_params(axis='y', labelsize=22)  # 设置 y 轴刻度字体大小为 12

    ax.grid(True, linestyle='--', alpha=0.6)

    # Create Legend
    # Create Legend
    legend_elements = []
    sorted_sfs = sorted(SF_COLORS.keys())  # From 7 to 12

    # Add SF elements in ascending order
    for sf in sorted_sfs:
        legend_elements.append(plt.Line2D([0], [0], marker='o', color='w',
                                        label=f'SF{sf}',
                                        markerfacecolor=SF_COLORS[sf],
                                        markersize=14))

    # Add Gateway last
    legend_elements.append(plt.Line2D([0], [0], marker=GATEWAY_MARKER, color='w',
                                    label='Gateway',
                                    markerfacecolor=GATEWAY_COLOR,
                                    markersize=14))


    ax.legend(handles=legend_elements,
            loc='upper center',
            bbox_to_anchor=(0.5, 1.10),
            ncol=7,
            fontsize=16,
            handletextpad=0.2,      
            columnspacing=0.5     
            )

    # plt.tight_layout(rect=[0, 0.03, 1, 0.90])
    plt.tight_layout()

    fig_name = 'SF Distribution.png'
    plt.savefig(os.path.join(folder_path, fig_name),dpi = 600)

def tp_distribution(folder_path):
    TP_COLORS = {
        2: 'lightgray',          # Very light, near-white
        4: 'khaki',              # Yellowish
        6: 'mediumaquamarine',   # Aqua-green
        8: 'lightskyblue',       # Light blue
        10: 'cornflowerblue',    # Medium blue
        12: 'darkorange',        # Deep orange 
        14: 'crimson'            # Deep red 
    }
    GATEWAY_COLOR = 'red'
    GATEWAY_MARKER = '^'

    # --- Plotting ---
    fig, ax = plt.subplots(figsize=(9, 9))  # Make it square for equal aspect ratio

    # Plot Gateways
    ax.scatter(ParameterConfig.GW.x, ParameterConfig.GW.y,
                marker=GATEWAY_MARKER, color=GATEWAY_COLOR, s=150, zorder=10, label="Gateway")

    # Plot Nodes
    for node in nodes:
        color = TP_COLORS.get(node.tp, 'grey')  # Default to grey if TP not in map

        ax.scatter(node.x, node.y, color=color, s=40, alpha=0.8)

    # --- Customize Plot ---
    ax.set_aspect('equal', adjustable='box')

    num_ticks = 5
    x_tick_positions = np.linspace(-radius, radius, num_ticks)
    ax.set_xlabel("Distance (m)", fontsize=12)
    ax.set_xticks(x_tick_positions)
    ax.set_xticklabels([f"{tick:.0f}" for tick in x_tick_positions])
    ax.set_xlim(-radius * 1.1, radius * 1.1)

    y_tick_positions = np.linspace(-radius, radius, num_ticks)
    ax.set_ylabel("Distance (m)", fontsize=12)
    ax.set_yticks(y_tick_positions)
    ax.set_yticklabels([f"{tick:.0f}" for tick in y_tick_positions])
    ax.set_ylim(-radius * 1.1, radius * 1.1)

    ax.grid(True, linestyle='--', alpha=0.6)

    # Create Legend
    legend_elements = []
    sorted_tps = sorted(TP_COLORS.keys())  # Sort TPs in ascending order
    for tp in sorted_tps:
        legend_elements.append(plt.Line2D([0], [0], marker='o', color='w',
                                          label=f'TP{tp}dBm',
                                          markerfacecolor=TP_COLORS[tp],
                                          markersize=8))
    legend_elements.append(plt.Line2D([0], [0], marker=GATEWAY_MARKER, color='w',
                                      label='Gateway',
                                      markerfacecolor=GATEWAY_COLOR,
                                      markersize=10))

    ax.legend(handles=legend_elements,
              loc='upper center',
              bbox_to_anchor=(0.5, 1.15),
              ncol=len(legend_elements) // 2 + 2,
              fontsize=10)

    plt.tight_layout(rect=[0, 0.03, 1, 0.90])
    fig_name = 'TP Distribution.png'
    plt.savefig(os.path.join(folder_path, fig_name))
    plt.show()

 