import json
from urllib.request import urlopen, Request
from github import Github
import csv
import pandas as pd
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

csv_repoinfo = 'github_repos_metrics.csv'
csv_externalcontr = 'github_externalcontr.csv'
csv_githubbasicstats = "github_repobasicmetrics.csv"
csv_uniquecollabs = "github_uniquecollaborators.csv"


def getOrgMembers(authToken):
    g = Github(authToken)
    namesmembers = []
    text_file = open("memblist.txt", "r")
    loginmembers = text_file.read().split(',')
    for orgs in g.get_user().get_orgs():
        for memb in orgs.get_members():
            if memb.login not in loginmembers:
                loginmembers.append(memb.login)
    for member in loginmembers:
        url_user = "https://api.github.com/users/" + member
        request = Request(url_user)
        request.add_header('Authorization', 'token %s' % authToken)
        response = urlopen(request)
        r_user = json.load(response)
        if r_user["name"] != None:
            namesmembers.append(r_user["name"])
    return loginmembers, namesmembers


def getRepoStatsContributions(authToken, notparsedrepo):
    g = Github(authToken)
    with open("github_RepoStatsContributions.csv", 'w', encoding='utf-8') as csvfile:
        df = pd.DataFrame(columns=["# loop", 'repo name', 'week', 'additions', "deletions", "commits", "author", "is a member?"])
        csvwriter = csv.writer(csvfile, delimiter=',')
        loginmembers, namesmembers = getOrgMembers(authToken)
        company = g.get_user().company
        company = company.strip("@")
        company = company.strip(" ")
        csvwriter.writerow(["# loop", 'repo name', 'week', 'additions', "deletions", "commits", "author", "is a member?"])
        for repo in g.get_user().get_repos():
            if repo.name != notparsedrepo:
                if repo.fork == False and repo.private == False and repo.full_name[:len(company)] == company:
                    count = 0
                    reponame = repo.name
                    print("\n","Working on repo:", reponame)
                    try:
                        for stat in repo.get_stats_contributors():
                            author = str(stat.author)
                            author = (author.replace('NamedUser(login="',"")).replace('")', "")
                            for week in stat.weeks:
                                count += 1
                                date = str(week.w)
                                date = date[:10]
                                if author in loginmembers:
                                    print(".", end=" ")
                                    try:
                                        csvwriter.writerow([count, reponame, date, week.a, week.d, week.c, author, "yes"])
                                    except:
                                        print("error")
                                else:
                                    print(".", end=" ")
                                    try:
                                        csvwriter.writerow([count, reponame, date, week.a, week.d, week.c, author, "no"])
                                    except:
                                        print("error2")
                    except:
                        print("none")
                        csvwriter.writerow([count, reponame, 0, 0, 0, 0, 0, "n/a"])


def uniqueCollabs(authToken):
    g = Github(authToken)
    with open(csv_uniquecollabs, "w", encoding="utf-8") as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',')
        csvwriter.writerow(["name", "login", "is a member of the organization?"])
        loginmembers, namesmembers = getOrgMembers(authToken)
        nameslist=[]
        company = g.get_user().company
        company = company.strip("@")
        company = company.strip(" ")
        for repo in g.get_user().get_repos():
            count = 0
            if repo.fork == False and repo.private == False and repo.full_name[:len(company)] == company:
                for commit in repo.get_commits():
                    count += 1
                    try:
                        author = commit.author
                        name = commit.author.name
                        if name not in nameslist:
                            author = str(author)
                            nameslist.append(name)
                            author = author.replace('")', '')
                            author = author.replace('NamedUser(login="', '')
                            if author not in loginmembers:
                                csvwriter.writerow([name, author, "no"])
                                print(name, "|", author, "| no")
                            else:
                                csvwriter.writerow([name, author, "yes"])
                                print(name, "|", author, "| yes")
                    except:
                        count+=1


def getBasicRepoStats(user, authToken):
    g = Github(authToken)
    with open(csv_githubbasicstats, "w", encoding="utf-8") as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=",")
        csvwriter.writerow(["count", "repo", "forks", "stars", "watches", "commits", "collaborators", "description"])
        url_repos = "https://api.github.com/users/" + user + "/orgs"
        request = Request(url_repos)
        request.add_header("Authorization", "token %s" % authToken)
        response = urlopen(request)
        r_user = json.load(response)
        for item in r_user:
            org = item["login"]
        for i in range(1, 21):
            url_orgrepos = "https://api.github.com/orgs/" + org + "/repos?page=" + str(i) + "&per_page=100"
            request = Request(url_orgrepos)
            request.add_header("Authorization", "token %s" % authToken)
            response = urlopen(request)
            r_orgs = json.load(response)
            count = 0
            for item in r_orgs:
                cont_colabs = 0
                cont_commits = 0
                if item["fork"] == False and item["private"] == False:
                    count += 1
                    colabs_url = item["contributors_url"]
                    request = Request(colabs_url)
                    request.add_header("Authorization", "token %s" % authToken)
                    response = urlopen(request)
                    r_colabs = json.load(response)
                    for col in r_colabs:
                        cont_colabs += 1
                    for j in range(1, 21):
                        commits_url = str(item["commits_url"])
                        commits_url = commits_url[:-6]
                        commits_url = commits_url + "?page=" + str(j) + "&per_page=100"
                        request = Request(commits_url)
                        request.add_header("Authorization", "token %s" % authToken)
                        response = urlopen(request)
                        r_commits = json.load(response)
                        for comm in r_commits:
                            cont_commits += 1
                    csvwriter.writerow([count, item["name"], item["forks_count"], item["stargazers_count"], item["watchers_count"], cont_commits, cont_colabs, item["description"]])
                    print(count, " ", item["name"], "|", item["forks_count"], "forks |", item["stargazers_count"], "stars |", item["watchers_count"], " watchers |", cont_commits, "commits |", cont_colabs, "collaborators |",
                        item["description"])


currenttoken = input("Please provide personal access token --> ")
currentuser = input("Please provide username --> ")
wontparse = input("Name of the repo not to be parsed --> ")

getOrgMembers(currenttoken)
getRepoStatsContributions(currenttoken, wontparse)
getBasicRepoStats(currentuser, currenttoken)