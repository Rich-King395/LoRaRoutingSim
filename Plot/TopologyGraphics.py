import matplotlib.pyplot as plt
from ParameterConfig import *
import ParameterConfig

def Mesh_Topology():
    if (graphics == 1):
        # graphics for node
        for node in ParameterConfig.nodes:
            if node.HopCount == 1:
                color = 'red'
            elif node.HopCount == 2:
                color = 'green'
            elif node.HopCount == 3:
                color = 'blue'
            else:
                color = 'gray'  # Default color for other hop counts
            
            ax.add_artist(plt.Circle((node.x, node.y), 40, fill=True, color=color))
            ax.text(node.x + 5, node.y + 5, str(node.ID), fontsize=9, ha='left', va='bottom')  # Add node ID above the node
            
            if link_line:
                # Draw dashed lines to parent nodes
                for parent in node.ParentSet:
                    ax.plot([node.x, parent.x], [node.y, parent.y], 'k--', linewidth=1)  # Dashed line to parent

        # graphics for base station
        ax.scatter(ParameterConfig.GW.x, ParameterConfig.GW.y,
                    marker='^', color='red', s=100, zorder=10, label="Gateway")
        ax.text(ParameterConfig.GW.x + 5, ParameterConfig.GW.y + 5, str(ParameterConfig.GW.ID), fontsize=9, ha='left', va='bottom')  # Add GW ID

        plt.xlim([-radius, radius])
        plt.ylim([-radius, radius])
        plt.draw()
        plt.pause(0.001)  # Add a short pause to allow the plot to update

        plt.show(block=True)  # Keep the plot window open until it is closed by the user


def Topology_Graphics(nodes):
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_aspect('equal', adjustable='box')
    ax.set_title("Network Topology", fontsize=16)
    
    artist_to_node = {}
    
    current_annotation = None

    for node in Devices:
        if node.HopCount == 0: 
            artist = ax.scatter(node.x, node.y, marker='^', color='red', s=200, zorder=10, label="Gateway", picker=True)
            ax.text(node.x + 8, node.y + 8, f"GW-{node.ID}", fontsize=9, ha='left', va='bottom', weight='bold')
        else:
            if node.HopCount == 1:
                color = 'red'
            elif node.HopCount == 2:
                color = 'green'
            elif node.HopCount == 3:
                color = 'blue'
            else:
                color = 'gray'
            
            circle = plt.Circle((node.x, node.y), 40, fill=True, color=color, picker=True)
            artist = ax.add_artist(circle)
            
            ax.text(node.x + 10, node.y + 10, str(node.ID), fontsize=9, ha='left', va='bottom')

        artist_to_node[artist] = node

        for parent in node.ParentSet:
            ax.plot([node.x, parent.x], [node.y, parent.y], 'k--', linewidth=1, zorder=1)

    radius = ParameterConfig.radius
    ax.set_xlim(-radius, radius)
    ax.set_ylim(-radius, radius)
    ax.set_xticks(range(-radius, radius + 1, 1000))
    ax.set_yticks(range(-radius, radius + 1, 1000))


    def on_pick(event):
        nonlocal current_annotation
        
        if current_annotation:
            current_annotation.remove()
            current_annotation = None
            
        target_artist = event.artist
        if target_artist in artist_to_node:
            node = artist_to_node[target_artist]
            
            if node.ID == 0:
                info_text = (
                    f"Gateway\n"
                    f"ID:   {node.ID}\n"
                )
            else:
                info_text = (
                    f"ID:   {node.ID}\n"
                    f"Distance: {node.DisttoGW:.2f} m\n"
                    f"PDR:  {node.PDR:.2%}"
                )
                
            current_annotation = ax.annotate(
                info_text,
                xy=(node.x, node.y),
                xytext=(20, 20),
                textcoords="offset points",
                bbox=dict(boxstyle="round,pad=0.5", fc="yellow", alpha=0.9),
                arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=0.2", color="black")
            )
        
        fig.canvas.draw_idle()

    fig.canvas.mpl_connect('pick_event', on_pick)
    
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.show(block=True)
    plt.close()
    exit()
