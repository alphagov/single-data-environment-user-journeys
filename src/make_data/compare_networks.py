"""
Compare Source and Target Nodes Between The Structural and Functional NetworkX Graphs

Exploratory data analysis exploring the differences in source and target node pairs
between the structural, `G_structural`, and functional, `G_functional`, NetworkX graphs.
    - 001: How many and which edges exist in the functional network do not exist in the
           structural network?
    - 002: How many and which edges exist in the functional network do not exist in the
           structural network that do not include source: target pairs where both are
           `www.gov.uk`?
    - 003: Which edges exist in the structural network do not exist in the functional
           network?
    - 004: Which nodes exist in both the functional and structural graph?

Assumptions:
    - For 002, source: target pairs where both are `www.gov.uk` are removed. When
      creating `G_functional`, all `www.gov.uk` hostname page hits are included.
      When creating `G_structural`, only `www.gov.uk` hostname page hits are included
      if they are hyperlinked from a page on `account.gov.uk` or `signin.account.gov.uk`.
      Therefore, it is a fairer comparison to remove `www.gov.uk` source: target pairs.

Requirements:
    - Run in order: `001_create_structural_networkx_graph.py`,
                    `002_extract_observed_user_movements.py`,
                    `003_create_functional_networkx_graph.py`

"""

# Import modules
import networkx as nx

# Load data
G_structural = nx.read_gpickle("../../data/processed/G_structural.gpickle")
G_functional = nx.read_gpickle("../../data/processed/G_functional.gpickle")

# Prepare data: convert source and target nodes into key: value pairs
functional_dict = {}
for u, v, a in G_functional.edges(data=True):
    functional_dict[u] = v, a

structural_dict = {}
for u, v, a in G_structural.edges(data=True):
    structural_dict[u] = v, a

# 001: Which edges exist in the functional network do not exist in the structural
# network?
edges_functional = {
    k: functional_dict[k]
    for k in set(functional_dict) - set(structural_dict)
}
edges_functional
len(edges_functional)

# 002: Which edges exist in the functional network do not exist in the structural
# network that do not include key: value pairs where both are `www.gov.uk`
edges_functional_not_govuk = {
    k: v
    for k, v in edges_functional.items()
    if not k.startswith("https://www.gov") and v[0].startswith("https://www.gov")
}
edges_functional_not_govuk
len(edges_functional_not_govuk)

# 003: Which edges exist in the structural network do not exist in the functional
# network?
edges_structural = {
    k: structural_dict[k]
    for k
    in set(structural_dict) - set(functional_dict)
}
edges_structural
len(edges_structural)

# 004: Which nodes exist in both the functional and structural graph
functional_nodes = [node for node in G_functional.nodes]
nodes_both_networks = [node for node in G_structural.nodes if node in functional_nodes]
nodes_both_networks
len(nodes_both_networks)
