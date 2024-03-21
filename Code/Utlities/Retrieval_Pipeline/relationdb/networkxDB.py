import networkx as nx
import pickle
import os
from itertools import permutations


filename = r""

# --------------------------------------------------------------------------------------------

def getObj():
    """
    Load a NetworkX graph object from a pickle file if it exists, otherwise return an empty graph.

    :arg
        - filename (str): Name of the pickle file containing the graph.

    returns:
        - nx.Graph: Loaded graph object if the file exists, otherwise an empty graph.

    notes:
        - If the specified file exists, it is assumed to contain a NetworkX graph serialized using pickle.
        - The function returns the loaded graph object if the file exists.
        - If the file doesn't exist, an empty graph is returned.
    """
    if os.path.exists(filename):
        # If the file exists, load the graph from the pickle file
        with open(filename,"rb") as GObj:
            return pickle.load(GObj)
    else:
        # If the file doesn't exist, return an empty graph
        return nx.Graph()

# --------------------------------------------------------------------------------------------

def addRelations(GObj: nx.Graph, nodes: dict, edges: dict):
    """
    Add nodes and edges with attributes to a NetworkX graph and save it to a pickle file.

    args:
        - GObj (nx.Graph): NetworkX graph object to which nodes and edges will be added.
        - nodes (dict): Dictionary containing node names as keys and node attributes as values.
        - edges (dict): Dictionary containing edge tuples as keys (source, target) and edge attributes as values.
        - filename (str): Name of the pickle file to save the graph.

    notes:
        - The function modifies the graph object GObj in place by adding nodes and edges with attributes.
        - Nodes are added with the specified attributes.
        - Edges are added with the specified attributes.
        - The graph is then saved to a pickle file with the specified filename.
    """
    # Add nodes with attributes
    for node, attr in nodes.items():
        GObj.add_node(node, **attr)

    # Add edges with attributes
    for edge, attr in edges.items():
        GObj.add_edge(*edge, **attr)

    # Save the graph to a pickle file
    with open(filename, 'wb') as f:
        pickle.dump(GObj, f)

# --------------------------------------------------------------------------------------------

def getRelations(GObj: nx.Graph, target_nodes):
    """
    Retrieve relations between target nodes in a graph.

    args:
        - GObj (nx.Graph): NetworkX graph object.
        - target_nodes (list): List of target nodes.

    returns:
        - list: List of relations between target nodes along the shortest path.

    notes:
        - This function finds the shortest path visiting all target nodes exactly once.
        - Relations are extracted along the shortest path, including edge attributes and node attributes.
    """
    # Initialize variables to store relations and shortest path
    relations = []
    shortest_path = None
    shortest_path_length = float('inf')

    # Generate all possible permutations of target nodes
    perms = permutations(target_nodes)


    # Find shortest path visiting all target nodes exactly once
    for perm in perms:
        path_length = 0
        is_valid_path = True

        for i in range(len(perm) - 1):
            # Check if there is an edge between consecutive target nodes
            if not GObj.has_edge(perm[i], perm[i+1]):
                is_valid_path = False
                break
            # Compute the shortest path length between consecutive target nodes
            path_length += nx.shortest_path_length(GObj, source=perm[i], target=perm[i+1])

        # Check if the current path is valid and shorter than the current shortest path
        if is_valid_path and path_length < shortest_path_length:
            shortest_path_length = path_length
            shortest_path = perm


    # Extract relations and attributes along the shortest path
    for i in range(len(shortest_path) - 1):

        relations.append({
            'source': shortest_path[i],
            'target': shortest_path[i + 1],
            'edge_attributes': GObj.get_edge_data(source, target),
            'node1_attributes': GObj.nodes[source],
            'node2_attributes': GObj.nodes[target]
        })

    return relations
# --------------------------------------------------------------------------------------------



