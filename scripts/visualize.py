#!/usr/bin/env python3
"""
K-GRASP Visualize Script
Generates a PNG image from the RDF graph.
"""

import rdflib
import networkx as nx
import matplotlib.pyplot as plt
import sys
import os

def visualize(ttl_file, output_png):
    print(f"Loading graph from {ttl_file}...")
    g = rdflib.Graph()
    try:
        g.parse(ttl_file, format="turtle")
    except Exception as e:
        print(f"Error parsing {ttl_file}: {e}")
        return

    dg = nx.DiGraph()
    
    # Colors for different types
    node_colors = []
    
    # Prefix for simplification
    KGRASP = rdflib.Namespace("http://cos.ufrj.br/kgrasp/games#")
    
    # Extract nodes and edges
    for s, p, o in g:
        # We only want to visualize relations between instances or classes
        if isinstance(s, rdflib.URIRef) and isinstance(o, (rdflib.URIRef, rdflib.Literal)):
            s_label = str(s).split("#")[-1].split("/")[-1]
            p_label = str(p).split("#")[-1].split("/")[-1]
            
            if isinstance(o, rdflib.URIRef):
                o_label = str(o).split("#")[-1].split("/")[-1]
                dg.add_edge(s_label, o_label, label=p_label)
            else:
                # Literals as nodes? Or just ignore for structural view?
                # For populated view, we might want labels as node attributes
                pass

    if len(dg.nodes) == 0:
        print("Graph is empty, nothing to visualize.")
        return

    print(f"Generating visualization for {len(dg.nodes)} nodes and {len(dg.edges)} edges...")
    
    plt.figure(figsize=(20, 20))
    # Use a layout that handles many nodes better
    pos = nx.spring_layout(dg, k=0.3, iterations=50)
    
    nx.draw(dg, pos, with_labels=True, 
            node_size=1500, 
            node_color="lightblue", 
            font_size=7, 
            font_weight="bold", 
            arrows=True,
            alpha=0.8,
            edge_color="gray")
    
    edge_labels = nx.get_edge_attributes(dg, 'label')
    nx.draw_networkx_edge_labels(dg, pos, edge_labels=edge_labels, font_size=6)
    
    plt.title(f"K-GRASP Knowledge Graph: {os.path.basename(ttl_file)}")
    plt.savefig(output_png, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Visualization saved to {output_png}")

if __name__ == "__main__":
    ttl = sys.argv[1] if len(sys.argv) > 1 else "grafo_populado.ttl"
    out = sys.argv[2] if len(sys.argv) > 2 else "kgrasp_populated.png"
    visualize(ttl, out)
