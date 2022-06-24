"""
Create Directed NetworkX Functional Graph

Create a directed NetworkX functional graph based on observed user movements
represented in `user_journeys_df`. Returns a graph using a pandas.Dataframe
containing an edge list, e.g. the source page,  target page, and edge
attributes.

Assumptions:
    - All edges must have a sourcePagePath and a destinationPagePath. Where
      destinationPagePath does not exist, e.g. a user leaves ww.gov.uk, then
      the edge (source: target) does not exist.
    - The edgeWeight represents the number of session hits that visit the target
      page from the source page.

Returns:
    A directed NetworkX graph `G_functional`

Requirements:
    Run `002_extract_observed_user_movements.py`
"""

# Import modules
import networkx as nx

# Load data
df = nx.read_gpickle("../data/interim/user_journeys_df.gpickle")

# Combine hostname and sourcePagePath
df["sourcePagePath"] = "https://" + df["hostname"] + df["pagePath"]

# Find the destination pagePath
df["destinationPagePath"] = (
    df.sort_values(by=["sessionId", "hitNumber"], ascending=True)
    .groupby(["sessionId"])["sourcePagePath"]
    .shift(-1)
)

df = df[["sessionId", "sourcePagePath", "destinationPagePath"]]

# Count the number of user sessions that visit a sourcePagePath to
# destinationPagePath
df = (
    df.groupby(["sourcePagePath", "destinationPagePath"], dropna=False)
    .sessionId.nunique()
    .reset_index(name="edgeWeight")
    .sort_values(by=["edgeWeight"], ascending=False)
    .dropna()
)

# Create NetworkX directed graph
G_functional = nx.from_pandas_edgelist(
    df, "sourcePagePath", "destinationPagePath", "edgeWeight", create_using=nx.DiGraph
)

# Graph functions
nx.info(G_functional)
nx.draw(G_functional, with_labels=False)

# Save graph
nx.write_gpickle(G_functional, "../data/processed/G_functional.gpickle")
