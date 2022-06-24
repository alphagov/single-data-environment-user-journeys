"""
Extract Observed User Movements Across Domains

This approach retrieves page hits that visit `www.gov.uk and a `seed_hosts`
domain(s) page in the same session, from Google BigQuery. It retrieves all page hits
in a session.

Assumptions:
    - Only page hits are included
    - Print pages are not included

Args:
    - start_date: String. The start date for the session hit data
    - end_date: String. The end date for the session hit data
    - seed_hosts: String. A list of URL slugs that host the cross-domain data
    - remove_query_parameters: Boolean expression. Set to TRUE if query
        parameters in the slug following `?` are to be removed

Returns:
    A pandas.DataFrame containing all page hits of sessions that visit a
    `seed_hosts` domain(s) and `www.gov.uk`

Requirements:
    You must be able to use Google Cloud Platform through code
    on your local machine and have the correct permissions to access
    `govuk-bigquery-analytics` project.
    See: https://docs.data-community.publishing.service.gov.uk/analysis/google-cloud-platform/#use-gcp-through-the-command-line-on-your-local-machine
"""

# Import modules
from google.cloud import bigquery

# Set variables
start_date = "20220524"
end_date = "20220524"
seed_hosts = ["account.gov.uk", "signin.account.gov.uk"]
remove_query_parameters = True

# Construct a BigQuery client object, define query parameters, define
# query, make an API request, and create a pandas.DataFrame
client = bigquery.Client(project="govuk-bigquery-analytics")

job_config = bigquery.QueryJobConfig(
    query_parameters=[
        bigquery.ScalarQueryParameter("startDate", "STRING", start_date),
        bigquery.ScalarQueryParameter("endDate", "STRING", end_date),
        bigquery.ArrayQueryParameter("seedHosts", "STRING", seed_hosts),
        bigquery.ScalarQueryParameter(
            "removeQueryParameters", "BOOL", remove_query_parameters
        ),
    ]
)

query = """
WITH
    primary_data AS (
        SELECT
            hits.hitNumber,
            IF(@removeQueryParameters, REGEXP_REPLACE(hits.page.pagePath, r'[?#].*', ''), hits.page.pagePath) AS pagePath,
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

    -- out of those sessions that visit at least one `seed_host`, which sessions also visit `www.gov.uk`
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

user_journeys_df = client.query(query, job_config=job_config).to_dataframe()
user_journeys_df.to_pickle("../data/interim/user_journeys_df.gpickle")
