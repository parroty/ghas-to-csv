#!/usr/bin/env python3

"""
This file holds the main function that does all the things.

Inputs:
- GitHub API endpoint (assumes github.com if not specified or run within GHES/GHAE)
- PAT of appropriate scope (assumes the workflow token if not specified)
- Report scope ("enterprise", "organization", "repository")
- Enterprise slug OR organization name OR repository name

Outputs:
- CSV file of secret scanning alerts
- CSV file of code scanning alerts

TODO: dependabot alerts
"""

# Import modules
from src import code_scanning, dependabot, enterprise, secret_scanning
import os

# Read in config values
if os.environ.get("GITHUB_API_ENDPOINT") is None:
    api_endpoint = "https://api.github.com"
else:
    api_endpoint = os.environ.get("GITHUB_API_ENDPOINT")

if os.environ.get("GITHUB_SERVER_URL") is None:
    url = "https://github.com"
else:
    url = os.environ.get("GITHUB_SERVER_URL")

if os.environ.get("GITHUB_PAT") is None:
    github_pat = os.environ.get("GITHUB_TOKEN")
else:
    github_pat = os.environ.get("GITHUB_PAT")

if os.environ.get("GITHUB_REPORT_SCOPE") is None:
    report_scope = "repository"
else:
    report_scope = os.environ.get("GITHUB_REPORT_SCOPE")

if os.environ.get("SCOPE_NAME") is None:
    scope_name = os.environ.get("GITHUB_REPOSITORY")
else:
    scope_name = os.environ.get("SCOPE_NAME")

# Do the things!
if __name__ == "__main__":
    if report_scope == "enterprise":
        # secret scanning
        secrets_list = secret_scanning.get_enterprise_secret_scanning_alerts(
            api_endpoint, github_pat, scope_name
        )
        secret_scanning.write_enterprise_secrets_list(secrets_list)
        # code scanning
        if enterprise.get_enterprise_version(api_endpoint) != "GHEC":
            repo_list = enterprise.get_repo_report(url, github_pat)
            cs_list = code_scanning.list_enterprise_server_code_scanning_alerts(
                api_endpoint, github_pat, repo_list
            )
            code_scanning.write_enterprise_server_cs_list(cs_list)
        else:
            cs_list = code_scanning.list_enterprise_cloud_code_scanning_alerts(
                api_endpoint, github_pat, scope_name
            )
            code_scanning.write_enterprise_cloud_cs_list(cs_list)

    elif report_scope == "organization":
        # code scanning
        cs_list = code_scanning.list_org_code_scanning_alerts(
            api_endpoint, github_pat, scope_name
        )
        code_scanning.write_org_cs_list(cs_list)
        # secret scanning
        secrets_list = secret_scanning.get_org_secret_scanning_alerts(
            api_endpoint, github_pat, scope_name
        )
        secret_scanning.write_org_secrets_list(secrets_list)
    elif report_scope == "repository":
        # code scanning
        cs_list = code_scanning.list_repo_code_scanning_alerts(
            api_endpoint, github_pat, scope_name
        )
        code_scanning.write_repo_cs_list(cs_list)
        # dependabot alerts
        if enterprise.get_enterprise_version(api_endpoint) == "GHEC":
            dependabot_list = dependabot.list_repo_dependabot_alerts(
                api_endpoint, github_pat, scope_name
            )
            dependabot.write_repo_dependabot_list(dependabot_list)
        else:
            pass
        # secret scanning
        secrets_list = secret_scanning.get_repo_secret_scanning_alerts(
            api_endpoint, github_pat, scope_name
        )
        secret_scanning.write_repo_secrets_list(secrets_list)
    else:
        exit("invalid report scope")
