# GitHub Metrics

**Notice:** `urllib` already migrated to `requests` library. 

I created this repo to gather some metrics for [sourced{d}](https://github.com/src-d/).
I used [GitHub’s REST API v3](https://developer.github.com/v3/) and [PyGitHub](http://pygithub.readthedocs.io) to develop the Python scripts.

There are 2 Python scripts.

-------

The `github_metrics.py` script runs the functions:

**1) `list_orgs(token)`**

function that returns a list of the organizations the user belongs to.


**2) `list_org_members(org, token)`**

function that builds a list with the members of an organization inside GitHub. Only current members are listed. It returns one list with members names and other list with members logins (usernames).


**3) `export_code_frequency(directory, org, token)`**

function that gather statistics for all repositories in an organization, by week/user/repo, and returns a csv file with: name of the repository, week in question, number of additions, number of deletions, author of such commit and if the author is a member or not of the organization.


**4) `list_unique_collaborators(directory, org, token)`**

function that returns the number of unique collaborators of an organization (for all its repos), with the information if the collaborator is a member of the organization or not.


**5) `export_community_engagement(directory, org, token)`**

function that gather basic metrics for all repos of an organization, such as number of forks, stars, commits and collaborators. The function returns a csv file with these informations for each repo.


You execute the file on command line by typing:
```
$ pip install -r requirements.txt
$ python github_metrics.py -t [GITHUB-TOKEN] -o [ORGANIZATION NAME]
```

-------

The script `export_traffic.py` runs the functions:

**1) `test_push_access(org, token)`**

function that will check which repositories your token has push access to, inside the specified organization. It returns two lists: one with the repositories that the token doesn't have push access to, and other with the repos the token has access to.

**2) `export_traffic(directory, org, repos_ok, token)`**

function that exports the traffic from GitHub repos that your token has push access to, for the last 14 days. It will create a csv file for the following metrics: traffic (views), clones, paths and referrers. Please check [further documentation](https://developer.github.com/v3/repos/traffic/) from GitHub.

**3) `relevantrepos_noaccess(numstars, repos_noaccess, organization, authToken)`** 
function that checks which repositories over `numstars` your token doesn't have access to, and returns a dictionary with the name of the repo and its number of stars.

You execute the file on command line by typing:
```
$ python export_traffic.py -t [GITHUB-TOKEN] -o [ORGANIZATION NAME]
```

For all functions, you have to input your authorization token, that is provided by GitHub at [https://github.com/settings/tokens](https://github.com/settings/tokens)

[![Analytics](https://ga-beacon.appspot.com/UA-109670866-1/some-github-metrics/readme?useReferer&utm_source=google&utm_medium=somegithub)](https://github.com/igrigorik/ga-beacon)
