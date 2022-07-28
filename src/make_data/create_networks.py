import datetime

import pandas as pd
import networkx as nx
from google.cloud import bigquery


def extract_observed_movements(start_date, end_date, seed_hosts, query_parameters):
    """
    Extract observed user movements across domains.

    This approach retrieves all page hits that visit `www.gov.uk` and a
    `seed_hosts` domain(s) page in the same session, from Google BigQuery.
    It retrieves all page hits in a session.

    Parameters
    ----------
    start_date : str
        Session hit data is extracted from this date, format YYYYMMDD.
    end_date : str
        Session hit data is extracted to this date, format YYYYMMDD.
    seed_hosts : list of str
        A list of URL slugs that host the cross-domain data.
    query_parameters: boolean
        Set to FALSE to remove query parameters following '?' in all slugs.

    Returns
    -------
    pandas.DataFrame
        Contains all page hits of all sessions that visit a `seed_hosts` domain(s)
        and `www.gov.uk` in page hit ascending order.

    Example
    -------
    >>> user_journeys_df = extract_observed_movements("20220505", "20220506",
                           ["account.gov.uk"], query_parameters=False)
    >>> user_journeys_df
            sessionId	hitNumber	pagePath	                hostname
    0	    10154	    1	        /government/organisations	www.gov.uk
    1	    10154	    2	        /enter-email            	account.gov.uk
    2	    10154	    7	        /government/news/...	    www.gov.uk
    3	    10154	    8	        /account-manage 	        account.gov.uk
    ...	    ...	        ...	        ...	                        ...
    1284	98793	    5	        /government/organisations   www.gov.uk
    1285	98793	    6	        /government/publication 	www.gov.uk
    1285	98793	    8	        /email/subscriptions...	    www.gov.uk
    1285	98793	    10	        /sign-in-or-create	        account.gov.uk
    1285	98793	    12	        /enter-email-create	        account.gov.uk
    """
    # Raise error if start and/or end date is not a string in the following format
    # YYYYMMDD
    if not isinstance(start_date, str) or not isinstance(end_date, str):
        raise TypeError(
            "start_date and end_date must be a string in the format YYYYMMDD"
        )

    try:
        datetime.datetime.strptime(start_date, "%Y%m%d")
    except ValueError:
        raise ValueError("Incorrect start_date format, should be YYYYMMDD")

    try:
        datetime.datetime.strptime(end_date, "%Y%m%d")
    except ValueError:
        raise ValueError("Incorrect end_date format, should be YYYYMMDD")

    # Construct a BigQuery client object, and define query parameters
    client = bigquery.Client(project="govuk-bigquery-analytics")

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("startDate", "STRING", start_date),
            bigquery.ScalarQueryParameter("endDate", "STRING", end_date),
            bigquery.ArrayQueryParameter("seedHosts", "STRING", seed_hosts),
            bigquery.ScalarQueryParameter("queryParameters", "BOOL", query_parameters),
        ]
    )

    # Define query
    query = """
    WITH
        primary_data AS (
            SELECT
                hits.hitNumber,
                IF(@queryParameters,
                    REGEXP_REPLACE(hits.page.pagePath, r'[?#].*', ''),
                    hits.page.pagePath) AS pagePath,
                CONCAT(fullVisitorId, "-", CAST(visitId AS STRING)) AS sessionId,
                hits.page.hostname,
            FROM `govuk-bigquery-analytics.87773428.ga_sessions_*`
            CROSS JOIN UNNEST(hits) AS hits
            WHERE _TABLE_SUFFIX BETWEEN @startDate AND @endDate
                AND hits.page.pagePath NOT LIKE "/print%"
                AND hits.type = 'PAGE'
            ),

        -- sessions which visit at least one `seed_hosts`
        distinct_sessions_seed_host AS (
            SELECT DISTINCT
                sessionId
            FROM primary_data
            WHERE hostname IN UNNEST(@seedHosts)
            GROUP BY sessionId, pagePath
        ),

        -- all page hits from sessions that visit at least one `seed_hosts`
        all_hits_seed_host AS (
            SELECT
                sessionId,
                hitNumber,
                pagePath,
                hostname
            FROM primary_data
            WHERE sessionId IN (SELECT sessionId FROM distinct_sessions_seed_host)
        ),

        -- out of those sessions that visit at least one `seed_host`, which sessions
        -- also visit `www.gov.uk`
        distinct_sessions_all AS (
            SELECT DISTINCT
                sessionId
            FROM all_hits_seed_host
            WHERE hostname = 'www.gov.uk'
        )

        -- all page hits of sessions that also visit `www.gov.uk`
        SELECT
            *
        FROM all_hits_seed_host
        WHERE sessionId IN (SELECT sessionId FROM distinct_sessions_all)
        ORDER BY sessionId, hitNumber
    """

    # Make an API request, and return a pandas.DataFrame
    return client.query(query, job_config=job_config).to_dataframe()


def create_functional_network(user_journeys_df):
    """
    Create directed NetworkX functional graph.

    Create a directed NetworkX functional graph based on real, observed user
    movements.

    Parameters
    ----------
    user_journeys_df : pandas.DataFrame
        Contains all page hits of all sessions that visit a `seed_hosts` domain(s)
        and `www.gov.uk` in page hit ascending order.

    Returns
    -------
    networkx.DiGraph
        Directed NetworkX functional graph containing an edge list, i.e. the source
        page, target page, and edge attributes.

    Example
    -------
    >>> data = {'sessionId': [10154, 10154, 10154, 98793, 98793],
                'hitNumber': [1, 3, 5, 2, 6],
                'pagePath': ['/enter-email', '/government/news/...',
                    '/account-manage', '/government/publication',
                    '/sign-in-or-create'],
                'hostname': ['www.gov.uk', 'www.gov.uk', 'account.gov.uk',
                    'www.gov.uk', 'account.gov.uk']}
    >>> user_journeys_df = pd.DataFrame(data)
    >>> G_functional = create_functional_network(user_journeys_df)
    >>> nx.info(G_functional)
    'DiGraph with 5 nodes and 3 edges'
    """
    journeys_df = user_journeys_df.copy()

    # Raise error if user_journeys_df is not a pandas.DataFrame with the columns
    # sessionId, hitNumber, pagePath, hostname
    if not isinstance(df, pd.DataFrame):
        raise TypeError("user_journeys_df must be a pandas.DataFrame")

    if not all(
        col in df.columns for col in ["sessionId", "hitNumber", "pagePath", "hostname"]
    ):
        raise ValueError(
            "user_journeys_df must be a pandas.DataFrame with the columns "
            "sessionId, hitNumber, pagePath, hostname"
        )

    # Combine hostname and sourcePagePath
    journeys_df["sourcePagePath"] = "https://" + journeys_df["hostname"] + journeys_df["pagePath"]

    # Find the destination pagePath
    journeys_df["destinationPagePath"] = (
        journeys_df.sort_values(by=["sessionId", "hitNumber"], ascending=True)
        .groupby(["sessionId"])["sourcePagePath"]
        .shift(-1)
    )

    journeys_stripped_df = journeys_df[["sessionId", "sourcePagePath", "destinationPagePath"]]

    # Count the number of user sessions that traverse from a sourcePagePath to
    # a destinationPagePath
    journeys_stripped_df = (
        journeys_stripped_df.groupby(["sourcePagePath", "destinationPagePath"], dropna=False)
        .sessionId.nunique()
        .reset_index(name="edgeWeight")
        .sort_values(by=["edgeWeight"], ascending=False)
        .dropna()
    )

    # Create NetworkX directed graph
    G_functional = nx.from_pandas_edgelist(
        df,
        "sourcePagePath",
        "destinationPagePath",
        "edgeWeight",
        create_using=nx.DiGraph,
    )

    return G_functional
