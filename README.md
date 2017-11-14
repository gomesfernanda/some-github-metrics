## GitHub Metrics

I created this repo to gather some metrics for the company I work for.
I used [GitHub’s REST API v3](https://developer.github.com/v3/) and [PyGitHub](http://pygithub.readthedocs.io) to develop the Python scripts.

There are 4 functions on this repository:

**1) `getOrgMembers(authToken)`**

function that builds a list with the members of an organization inside GitHub. Only current members are listed. It returns one list with members names and other list with members logins


**2) `getRepoStatsContributions(authToken)`**

function that gather statistics for all repositories in an organization, by week/user/repo, and returns a csv file with: name of the repository, week in question, number of additions, number of deletions, author of such commit and if the author is a member or not of the community.


**3) `uniqueCollabs(authToken)`**

function that returns the number of unique collaborators of an organization (for all its repos), with the information if the collaborator is a member of the organization or not


**4) `getBasicRepoStats(user, authToken)`**

function that gather basic metrics for all repos of an organization, such as number of forks, number of stars, number of commits and number of collaborators. The function returns a csv file with these informations for each repo


For all functions, you have to input your authorization token, that is provided by GitHub at [https://github.com/settings/tokens](https://github.com/settings/tokens)

[![Analytics](https://ga-beacon.appspot.com/UA-109670866-1/some-github-metrics/readme)](https://github.com/igrigorik/ga-beacon)
