import pandas as pd


def format_journeys(G_functional, G_structural):
    """
    Format functional and structural user journeys.

    Format structural intended journeys and functional user journeys to
    correspond for further processing.

    Parameters
    ----------
    G_functional : pandas.DataFrame
        must include columns 'sessionId', 'pagePath', 'hostname'
    G_structural : list of lists of str
        each list represents a user journey, or a simple path

    Returns
    -------
    functional_user_journeys : pandas.DataFrame
        Unique user journeys and the number of times they were traversed, in
        descending order
    structural_user_journeys : panda.DataFrame
        Unique user journeys and the number of times they were traversed. Note
        that as this is a structural graph, and no edge weights are included the
        number of times they were traversed = 0

    Example
    -------
    >>> G_functional = pd.DataFrame({'sessionId': [1056, 1056, 2234, 2234],
        'pagePath': ['/sign-in-or-create', '/enter-email', '/signed-out',
        '/manage'], 'hostname': ['www.gov.uk', 'www.gov.uk', 'www.gov.uk',
        'www.gov.uk']})
    >>> G_structural = [['https://www.gov.uk/sign-in-or-create',
        'https://www.gov.uk/enter-email'],
        ['https://www.gov.uk/sign-in', 'https://www.gov.uk/email/manage',
        'https://www.gov.uk/signed-out']]
    >>> functional_user_journeys, structural_user_journeys =
        format_journeys(G_functional, G_structural)
    >>> functional_user_journeys
        userJourney                             countUserJourney
    0   https://www.gov.uk/sign-in-or-create    1
        https://www.gov.uk/enter-email
    1   https://www.gov.uk/signed-out           1
        https://www.gov.uk/manage
    >>> structural_user_journeys
        userJourney                             countUserJourney
    0   https://www.gov.uk/sign-in-or-create    0
        https://www.gov.uk/enter-email
    1   https://www.gov.uk/sign-in              0
        https://www.gov.uk/email/manage
        https://www.gov.uk/signed-out
    """

    # Create new df representing all functional pagePaths and count by sessionId
    G_functional["sourcePagePath"] = (
        "https://" + G_functional["hostname"] + G_functional["pagePath"]
    )
    functional_user_journeys = pd.DataFrame(
        G_functional.groupby("sessionId")["sourcePagePath"].apply(" ".join)
    )
    functional_user_journeys = pd.DataFrame(
        functional_user_journeys.sourcePagePath.value_counts()
        .rename_axis("userJourney")
        .reset_index()
    ).rename(columns={"sourcePagePath": "countUserJourney"})

    # Create new df representing all structural pagePaths and count by sessionId
    structural_user_journeys = []
    for paths in G_structural:
        path = [" ".join(paths)]
        new_dict = dict.fromkeys(path, 0)
        structural_user_journeys.append(new_dict)

    structural_user_journeys = {
        k: v for d in structural_user_journeys for k, v in d.items()
    }
    structural_user_journeys = pd.DataFrame(
        structural_user_journeys.items(), columns=["userJourney", "countUserJourney"]
    )

    return (functional_user_journeys, structural_user_journeys)


def compare_journeys(functional_user_journeys, structural_user_journeys):
    """
    Compares structural and functional journeys.

    Provides the structural journey, and the full functional journey the
    structural journey appears in.

    Parameters
    ----------
    functional_user_journeys : pandas.DataFrame
        Unique user journeys. Must include a column name 'userJourney'
    structural_user_journeys : pandas.DataFrame
        Unique user journeys. Must include a column name 'userJourney'

    Returns
    -------
    same_journeys_df : pandas.DataFrame
        Provides the corresponding functional journey a structural journey
        appears in.

    struct_journeys_not_appear : list
        A list of structural journeys that do not appear in the functional
        journeys.

    Example
    -------
    >>> functional_user_journeys = pd.DataFrame({'userJourney':
        ['www.gov.uk/sign-in-or-create www.gov.uk/enter-email',
        'www.gov.uk/signed-out www.gov.uk/manage'],
        'countUserJourney': [1, 1]})
    >>> structural_user_journeys = pd.DataFrame({'userJourney':
        ['www.gov.uk/sign-in-or-create www.gov.uk/enter-email',
        'www.gov.uk/sign-in www.gov.uk/email/manage www.gov.uk/signed-out'],
        'countUserJourney': [0, 0]})
    >>> same_journeys_df, struct_journeys_not_appear =
        compare_journeys(functional_user_journeys, structural_user_journeys)
    >>> same_journeys_df
            structural journey	            functional journey
        0	www.gov.uk/sign-in-or-create    www.gov.uk/sign-in-or-create
            www.gov.uk/enter-email 	        www.gov.uk/enter-email
    >>> struct_journeys_not_appear
        ['www.gov.uk/sign-in www.gov.uk/email/manage www.gov.uk/signed-out']
    """
    # Structural journeys that appear in the functional journeys
    comparison1 = []
    comparison2 = []

    for string1 in structural_user_journeys["userJourney"]:
        for string2 in functional_user_journeys["userJourney"]:
            result = string1 in string2
            if result:
                comparison1.append(string1)
                comparison2.append(string2)

    same_journeys_df = pd.DataFrame()
    same_journeys_df["structural journey"] = comparison1
    same_journeys_df["functional journey"] = comparison2

    # Structural journeys that do not appear in the functional journeys
    struct_journeys_not_appear = list(
        set(structural_user_journeys["userJourney"]) - set(comparison1)
    )

    return (same_journeys_df, struct_journeys_not_appear)
