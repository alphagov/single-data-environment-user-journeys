import networkx as nx


def find_simple_paths(source, target, G, exclude_pages=None, cutoff=None, verbose=1):
    """
    Find all simple paths between all source and target pairs.

    A simple path is a path between the source and target node, with no repeated
    nodes. This function does not check that a path exists between source and
    target. There may be large number of simple paths in a graph. An example of
    a source and target pair is source[0] and target[0], and not source[0] and
    target[1].

    Parameters
    ---------
    source : list of str
        List of source nodes.
    target : list of str
        List of target nodes.
    G : NetworkX graph
    exclude_pages : list of str, optional
        Removes a simple path from the output if the path includes one one of
        these pages.
    cutoff : int, optional
        Depth to stop the search. Only paths of length <= cutoff are returned.
    verbose : boolean, default '1'
        1 for progress bars, 0 for no progress bars.

    Returns
    -------
    list of lists of str
        URL slugs traversing from source to target.

    Example
    -------
    >>> data = {'www.gov.uk/': ['www.gov.uk/browse'],
                'www.gov.uk/browse': ['www.gov.uk/']}
    >>> G = nx.from_dict_of_lists(data)
    >>> find_simple_paths(['www.gov.uk/', 'www.gov.uk/browse'],
                          ['www.gov.uk/browse', 'www.gov.uk/'],
                          G, cutoff=1, exclude_pages=None, verbose=0)
    [['www.gov.uk/', 'www.gov.uk/browse'],
    ['www.gov.uk/browse', 'www.gov.uk/']]
    """
    all_simple_paths = []

    for ind, url in enumerate(source):
        # Loop through all source and target pairs
        all_simple_paths.extend(
            nx.all_simple_paths(G, source[ind], target[ind], cutoff)
        )
        if verbose:
            print("Completed", ind + 1, "of", len(source))

    # Remove paths that contain a page in the exclude_pages list
    if exclude_pages:
        all_simple_paths = [
            path
            for path in all_simple_paths
            if not any(page in path for page in exclude_pages)
        ]

    return all_simple_paths


def rank_simple_paths(method, G, all_simple_paths, verbose=1):
    """ "
    Rank the order of all simple paths by a given method.

    Parameters
    ---------
    method : str
        Method to rank simple paths. Use 'shortest' to rank by the shortest path,
        or node centrality metrics: 'pageRank', 'betweenness', 'closeness', or
        'eigenvector'
    G : NetworkX graph
    all_simple_paths : list of lists of str
        List of lists of all simple paths.
    verbose : boolean, default '1'
        1 for progress bars, 0 for no progress bars.

    Returns
    -------
    list of lists of str
        Ranked simple paths, in descending order.

    Example
    -------
    >>> data = {'www.gov.uk/': ['www.gov.uk/browse'],
                'www.gov.uk/browse': ['www.gov.uk/', 'www.gov.uk/childcare']}
    >>> G = nx.from_dict_of_lists(data)
    >>> all_simple_paths = find_simple_paths(['www.gov.uk/', 'www.gov.uk/'],
                                             ['www.gov.uk/', 'www.gov.uk/browse'],
                                             G, verbose=0)
    >>> rank_simple_paths('shortest', G, all_simple_paths, verbose=0)
    [['www.gov.uk/', 'www.gov.uk/browse'],
     ['www.gov.uk/', 'www.gov.uk/browse', 'www.gov.uk/childcare']]
    """
    # Rank by shortest path
    if method == "shortest":
        all_simple_paths.sort(key=len)
        journeys_ranked_dict = all_simple_paths

    # Or, rank all page paths by a given method
    if method == "pageRank":
        ranking_method = nx.pagerank(G)
    elif method == "betweenness":
        ranking_method = nx.betweenness_centrality(G)
    elif method == "closeness":
        ranking_method = nx.closeness_centrality(G)
    elif method == "eigenvector":
        ranking_method = nx.eigenvector_centrality(G)

    # If method is not shortest
    if not method == "shortest":
        # convert all_simple_paths into a dict
        all_simple_paths_key = []

        for paths in all_simple_paths:
            path = [" ".join(paths)]
            new_dict = dict.fromkeys(path, 0)
            all_simple_paths_key.append(new_dict)

        all_simple_paths_dict = {
            k: v for d in all_simple_paths_key for k, v in d.items()
        }

        # get the sum of the method ranking for each journey
        for ind, key in enumerate(all_simple_paths_dict):

            # turn each key into a list of nodes
            key_list = key.split()
            temp_dict = {}

            for k in key_list:
                # if each url in key_list is each url in ranking_method
                if k in ranking_method:
                    # add the ranking_method metric to each url
                    temp_dict[k] = ranking_method[k]

            # if verbose, show progress
            if verbose:
                print("Completed", ind + 1, "of", len(all_simple_paths_dict))

            # create proportion of the ranking_method for each simple path journey
            all_simple_paths_dict[key] = sum(temp_dict.values()) / len(temp_dict)

        journeys_ranked = dict(
            sorted(
                all_simple_paths_dict.items(), key=lambda item: item[1], reverse=True
            )
        )

        # add comma after every string in dict key
        journeys_ranked_dict = {}
        for key, value in journeys_ranked.items():
            journeys_ranked_dict[key.replace(" ", ", ")] = value

    return journeys_ranked_dict
