"""
Bokeh Plot to Visualise Observed User Movements Across the Structural Network Graph

Assumptions:
    - The network is a directed graph
    - Edges are weighted, with weights representing the number of times a session has
      traversed the edge
    - The fundamental network is a structural network representing the pages hyperlinked
      to one another. A functional network is 'overlayed', representing real user
      movements across the structural network. As such, real user movements not in the
      structural network are removed.

Returns:
    An HTML file that opens in a browser, containing a Bokeh plot of the observed user
    movements across the structural network graph.

Requirements:
    - Run in order: `001_create_structural_networkx_graph.py`,
                    `002_extract_observed_user_movements.py`,
                    `003_create_functional_networkx_graph.py`
"""

# Import modules
import networkx as nx
from bokeh.io import show
from bokeh.models import Circle, MultiLine, NodesAndLinkedEdges
from bokeh.plotting import figure, from_networkx, save

"""
Prepare Data
"""

# Load graphs
G_structural = nx.read_gpickle("../../data/processed/G_structural.gpickle")
G_functional = nx.read_gpickle("../../data/processed/G_functional.gpickle")

# Remove nodes from `G_functional` that are not represented in `G_structural`
functional_nodes_list = [node for node in G_functional.nodes()]
structural_nodes_list = [node for node in G_structural.nodes()]
nodes_to_remove = [x for x in functional_nodes_list if x not in structural_nodes_list]
G_functional.remove_nodes_from(nodes_to_remove)

# Set up `G_functional` attributes for plotting
for url in G_functional.nodes:
    G_functional.nodes[url]["title"] = url
    G_functional.nodes[url]["network_colour"] = "red"

    list_of_all_in_edges = list(G_functional.in_edges(url, data=True))
    list_of_all_out_edges = list(G_functional.out_edges(url, data=True))

    list_of_in_edges = [[el[0], el[2]["edgeWeight"]] for el in list_of_all_in_edges]
    list_of_out_edges = [[el[1], el[2]["edgeWeight"]] for el in list_of_all_out_edges]

    G_structural.nodes[url]["user_movement_to"] = list_of_in_edges
    G_structural.nodes[url]["user_movement_from"] = list_of_out_edges

for source, target, data in G_functional.edges(data=True):
    data["network_edge_colour"] = "red"
    data["edge_highlight_colour"] = "orange"
    data["edge_alpha"] = 0.5

    if data["edgeWeight"] >= 2 and data["edgeWeight"] <= 10:
        data["edge_width"] = 3
    elif data["edgeWeight"] > 10 and data["edgeWeight"] <= 100:
        data["edge_width"] = 5
    elif data["edgeWeight"] > 100:
        data["edge_width"] = 10
    elif data["edgeWeight"] < 2:
        data["edge_width"] = 1

# Set up `G_structional` attributes for plotting
for url in G_structural.nodes:
    G_structural.nodes[url]["title"] = url
    G_structural.nodes[url]["network_colour"] = "blue"

    list_of_in_edges = [el[:1] for el in list(G_structural.in_edges(url))]
    list_of_out_edges = [el[1:] for el in list(G_structural.out_edges(url))]

    G_structural.nodes[url]["hyperlinks_to"] = list_of_out_edges
    G_structural.nodes[url]["hyperlinks_from"] = list_of_in_edges

for source, target, data in G_structural.edges(data=True):
    data["network_edge_colour"] = "black"
    data["edge_highlight_colour"] = "#027600"
    data["edge_alpha"] = 0.3
    data["edge_width"] = 1

# Combine graphs
# Note: `G_functional` will overwrite the same attributes as `G_structural`
G = nx.compose(G_structural, G_functional)

"""
Choose plot attributes
"""

# Choose colors for node and edge highlighting
node_highlight_color = "white"
edge_highlight_color = "green"

# Choose attributes from `G` network to size and color by
# Note: setting manual size (e.g. 10) or colour (e.g. 'skyblue') also allowed
color_by_this_attribute = "network_colour"
edge_color_by_this_attribute = "network_edge_colour"
edge_highlight_color_by_this_attribute = "edge_highlight_colour"
edge_alpha_by_this_attribute = "edge_alpha"
edge_width_by_this_attribute = "edge_width"

# Choose a title
title = "User movements across the `account` domain"

# Establish which categories will appear when hovering over each node
HOVER_TOOLTIPS = [
    ("Title", "@title"),
    ("Hyperlinks to", "@hyperlinks_to"),
    ("Hyperlinks from", "@hyperlinks_from"),
    ("User movement to", "@user_movement_to"),
    ("User movement from", "@user_movement_from"),
]

"""
Create Bokeh plot
"""

# Create a plot — set dimensions, toolbar, and title
plot = figure(
    tooltips=HOVER_TOOLTIPS,
    tools="pan,wheel_zoom,save,reset",
    active_scroll="wheel_zoom",
    title=title,
    plot_width=1400,
    plot_height=800,
)

# Create Bokeh plot using a networkx.Graph object
network_graph = from_networkx(G, nx.kamada_kawai_layout, center=(0, 0))

# Set node sizes and colours
network_graph.node_renderer.glyph = Circle(size=15, fill_color=color_by_this_attribute)

# Set node highlight colours
network_graph.node_renderer.hover_glyph = Circle(
    fill_color=node_highlight_color, line_width=2
)
network_graph.node_renderer.selection_glyph = Circle(
    fill_color=node_highlight_color, line_width=2
)

# Set edge opacity, colours, and widths
network_graph.edge_renderer.glyph = MultiLine(
    line_alpha=edge_alpha_by_this_attribute,
    line_width=edge_width_by_this_attribute,
    line_color=edge_color_by_this_attribute,
)

# Set edge highlight colours
network_graph.edge_renderer.selection_glyph = MultiLine(
    line_color=edge_highlight_color_by_this_attribute, line_width=1.5
)
network_graph.edge_renderer.hover_glyph = MultiLine(
    line_color=edge_highlight_color_by_this_attribute, line_width=1.5
)

# Highlight nodes and edges
network_graph.selection_policy = NodesAndLinkedEdges()
network_graph.inspection_policy = NodesAndLinkedEdges()

# Render, display, and save plot
plot.renderers.append(network_graph)
show(plot)
save(plot, filename=f"../../data/processed/{title} plot.html")
