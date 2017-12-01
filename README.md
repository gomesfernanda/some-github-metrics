# GitHub Metrics

**Notice:** `urllib` to be migrated to `requests` library. 

I created this repo to gather some metrics for [sourced{d}](https://github.com/src-d/).
I used [GitHub’s REST API v3](https://developer.github.com/v3/) and [PyGitHub](http://pygithub.readthedocs.io) to develop the Python scripts.

There are 5 functions on this repository:

**1) `getOrgs(token)`**

function that returns a list of the organizations the user belongs to.


**2) `getOrgMembers(org, token)`**

function that builds a list with the members of an organization inside GitHub. Only current members are listed. It returns one list with members names and other list with members logins (usernames).


**3) `getRepo_CodeFrequency(org, token, notparsedrepo=None)`**

function that gather statistics for all repositories in an organization, by week/user/repo, and returns a csv file with: name of the repository, week in question, number of additions, number of deletions, author of such commit and if the author is a member or not of the organization.


**4) `getUniqueCollabs(org, token)`**

function that returns the number of unique collaborators of an organization (for all its repos), with the information if the collaborator is a member of the organization or not.


**5) `getRepo_Community(org, token)`**

function that gather basic metrics for all repos of an organization, such as number of forks, stars, commits and collaborators. The function returns a csv file with these informations for each repo.


For all functions, you have to input your authorization token, that is provided by GitHub at [https://github.com/settings/tokens](https://github.com/settings/tokens)

[![Analytics](https://ga-beacon.appspot.com/UA-109670866-1/some-github-metrics/readme?useReferer&utm_source=google&utm_medium=somegithub)](https://github.com/igrigorik/ga-beacon)
