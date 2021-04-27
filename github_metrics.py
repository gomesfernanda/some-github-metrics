import argparse
from github import Github
import requests
import json
import csv
import os
import datetime
import socket
import pandas as pd

socket.setdefaulttimeout(60 * 60)
today = datetime.date.today()
todaystr = str(today)

def setup():
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--org", help="choose what company you what to see", required=True)
    parser.add_argument("-t", "--token", help="OAuth token from GitHub", required=True)
    args = parser.parse_args()
    return args

def list_orgs(authToken):
    g = Github(authToken)
    orgslist = []
    for orgs in g.get_user().get_orgs():
        orgslist.append(orgs.login)
    return orgslist

def list_org_members(org, authToken):
    s = requests.Session()
    s.headers.update({'Authorization': 'token ' + authToken})
    g = Github(authToken)
    namesmembers = []
    try:
        filename = "memblist_" + org + ".txt"
        text_file = open(filename, "r")
        loginmembers = text_file.read().split(',')
    except:
        loginmembers = []
    for orgs in g.get_user().get_orgs():
        if orgs.login == org:
            for memb in orgs.get_members():
                if memb.login not in loginmembers:
                    loginmembers.append(memb.login)
        else:
            next
    if loginmembers[0] == "":
        loginmembers.pop(0)
    for member in loginmembers:
        r = s.get("https://api.github.com/users/" + member)
        r_user = json.loads(r.text)
        try:
            if r_user["name"] != None:
                namesmembers.append(r_user["name"])
            else:
                namesmembers.append(r_user["login"])
        except:
            next
    return loginmembers, namesmembers

def export_code_frequency(directory, organization, authToken):
    totalrepos = 0
    g = Github(authToken)
    today = str(datetime.date.today())
    today = today.replace("-", "")
    allorgs = g.get_user().get_orgs()
    for orgs in allorgs:
        if orgs.login == organization:
            for repo in orgs.get_repos():
                if repo.fork == False and repo.private == False:
                    totalrepos +=1
    with open(directory + "/github_code_frequency_" + organization + "_" + today+ ".csv", 'w', encoding='utf-8') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',')
        csvwriter.writerow(
            ["count", "org", "repo", "week", "additions", "deletions", "commits", "author", "is a member"])
        loginmembers, namesmembers = list_org_members(organization, authToken)
        for orgs in allorgs:
            if orgs.login == organization:
                print("Gathering code frequency for all repos on", orgs.login)
                count = 0
                for repo in orgs.get_repos():
                    controws = 0
                    if repo.fork == False and repo.private == False:
                        count += 1
                        reponame = repo.name
                        try:
                            stats = repo.get_stats_contributors()
                            for stat in stats:
                                author = str(stat.author)
                                author = (author.replace('NamedUser(login="', "")).replace('")', "")
                                for week in stat.weeks:
                                    if week.c != 0:
                                        date = str(week.w)
                                        date = date[:10]
                                        if author in loginmembers:
                                            controws+=1
                                            try:
                                                csvwriter.writerow(
                                                    [count, orgs.login, reponame, date, week.a, week.d, week.c, author,
                                                     "yes"])
                                            except:
                                                print("error")
                                        else:
                                            controws += 1
                                            try:
                                                csvwriter.writerow(
                                                    [count, orgs.login, reponame, date, week.a, week.d, week.c, author,
                                                     "no"])
                                            except:
                                                print("error2")
                            print("[", str(count).zfill(2), "|", totalrepos, "] ", orgs.login, " | ", repo.name,  " | ", controws, " rows in the file")
                        except:
                            print("[", str(count).zfill(2), "|", totalrepos, "] ", orgs.login, " | ", repo.name, "| none")
                            csvwriter.writerow([count, orgs.login, reponame, 0, 0, 0, 0, 0, "n/a"])
            else:
                next

def export_community_engagement(directory, organization, authToken):
    g = Github(authToken)
    today = str(datetime.date.today())
    today = today.replace("-", "")
    totalrepos = 0
    allorgs = g.get_user().get_orgs()
    for orgs in allorgs:
        if orgs.login == organization:
            for repo in orgs.get_repos():
                if repo.fork == False and repo.private == False:
                    totalrepos += 1
    with open(directory + "/github_community_engagement_" + organization + "_" + today+ ".csv", 'w', encoding='utf-8') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',')
        csvwriter.writerow(
            ["date", "org", "repo", "forks", "stars", "commits", "collaborators"])
        for orgs in allorgs:
            if orgs.login == organization:
                print("Gathering community metrics for", orgs.login)
                count = 0
                for repo in orgs.get_repos():
                    try:
                        hascommits = repo.get_commits()[0]
                    except:
                        hascommits = False
                        print(repo.name, 'is empty')
                    countcommit = 0
                    countcollab = 0
                    if repo.fork == False and repo.private == False and hascommits != False:
                        count += 1
                        for commits in repo.get_commits():
                            countcommit += 1
                        for collab in repo.get_contributors():
                            countcollab += 1
                        print("[", str(count).zfill(2), "|", totalrepos, "]", repo.name, "|", countcommit, "commits |", repo.forks_count, "forks |",
                              repo.stargazers_count, "stars |", countcollab, "contributors")
                        csvwriter.writerow(
                            [todaystr, organization, repo.name, repo.forks_count, repo.stargazers_count, countcommit,
                             countcollab])

def list_unique_collaborators(directory, organization, authToken):
    g = Github(authToken)
    with open(directory + "/github_unique_collaborators_" + organization + ".csv", "w", encoding="utf-8") as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',')
        csvwriter.writerow(["name", "login", "name", "member of the org?"])
        loginmembers, namesmembers = list_org_members(organization, authToken)
        userslist = []
        nameslist = []
        allorgs = g.get_user().get_orgs()
        for orgs in allorgs:
            if orgs.login == organization:
                print("Gathering unique collaborators for", orgs.login)
                count = 0
                for repo in orgs.get_repos():
                    if repo.fork == False and repo.private == False:
                        for collab in repo.get_contributors():
                            if collab.login not in userslist:
                                userslist.append(collab.login)
                                if collab.name != None:
                                    nameslist.append(collab.name)
                                else:
                                    nameslist.append(collab.login)
                                count += 1
                                collablogin = collab.login
                                if collab.name == None:
                                    collabname = collab.login
                                else:
                                    collabname = collab.name
                                if collablogin in loginmembers:
                                    member = "yes"
                                else:
                                    member = "no"
                                print(str(count).zfill(2), "|", member, "|", collablogin, "|", collabname)
                                csvwriter.writerow([count, collablogin, collabname, member])

def main():
    args = setup()
    organization = args.org
    authToken = args.token
    g = Github(authToken)
    directory = "output/" + organization
    if not os.path.exists(directory):
        os.makedirs(directory)

    try:
        print("Valid token. Starting process. \n")
        list_org_members(organization, authToken)
        print("")
        export_code_frequency(directory, organization, authToken)
        print("")
        export_community_engagement(directory, organization, authToken)
    except Exception as e:
        print(e)


if __name__ == '__main__':
    main()