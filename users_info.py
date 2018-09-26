import argparse
from github import Github
import requests
import json
import csv
import os
import datetime

s = requests.Session()

import time

now = time.time()
today = datetime.date.today()
todaystr = str(today)


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


def get_rate_limit(authToken):
    g = Github(authToken)
    ratelimit = g.rate_limiting
    remaining = ratelimit[0]
    reset_time = g.rate_limiting_resettime
    minutes_left = (reset_time - now) / 60
    if remaining == 0:
        print(minutes_left)
    return remaining


def get_users_forked(members_list, authToken):
    g = Github(authToken)
    s.headers.update({'Authorization': 'token ' + authToken})
    orgs = g.get_user().get_orgs()
    with open("github_users_forked_" + todaystr + ".csv", 'w', encoding='utf-8') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',')
        csvwriter.writerow(
            ['Organization', 'Repo', 'Name', 'Username', 'Email', 'Type interaction'])
        for org in orgs:
            org_name = org.name
            org_login = org.login
            print("~~~~~~~~~~~~~~~~~~~~~~~~~~~ ", org_name, " ~~~~~~~~~~~~~~~~~~~~~~~~~~~\n")
            repos = org.get_repos()
            for i, repo in enumerate(repos):
                if repo.fork == False:
                    repo_name = repo.name
                    print("\nCollecting e-mails for", repo_name)
                    count = 0
                    forks = repo.get_forks()
                    for fork in forks:
                        forker_login = fork.owner.login
                        forker_name = fork.owner.name
                        forker_email = fork.owner.email
                        if forker_login not in members_list and forker_email != None:
                            count += 1
                            print(forker_email)
                            csvwriter.writerow([org_login, repo_name, forker_name, forker_login, forker_email, "fork"])
                    print(" -----", str(count), "emails collected")

def get_users_starred(members_list, authToken):
    g = Github(authToken)
    s.headers.update({'Authorization': 'token ' + authToken})
    orgs = g.get_user().get_orgs()
    with open("github_users_starred_" + todaystr + ".csv", 'w', encoding='utf-8') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',')
        csvwriter.writerow(
            ['Organization', 'Repo', 'Name', 'Username', 'Email', 'Type interaction'])
        for org in orgs:
            org_name = org.name
            org_login = org.login
            print("~~~~~~~~~~~~~~~~~~~~~~~~~~~ ", org_name, " ~~~~~~~~~~~~~~~~~~~~~~~~~~~\n")
            repos = org.get_repos()
            for i, repo in enumerate(repos):
                if repo.fork == False:
                    repo_name = repo.name
                    print("\nCollecting e-mails for", repo_name)
                    count = 0
                    stargazers = repo.get_stargazers()
                    for stargazer in stargazers:
                        stargazer_name = stargazer.name
                        stargazer_login = stargazer.login
                        stargazer_email = stargazer.email
                        if stargazer_login not in members_list and stargazer_email != None:
                            count += 1
                            print(stargazer_email)
                            csvwriter.writerow(
                                [org_login, repo_name, stargazer_name, stargazer_login, stargazer_email, "star"])
                    print(" -----", str(count), "emails collected")

def get_users_comitted(members_list, authToken):
    g = Github(authToken)
    s.headers.update({'Authorization': 'token ' + authToken})
    orgs = g.get_user().get_orgs()
    with open("github_users_commited_" + todaystr + ".csv", 'w', encoding='utf-8') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',')
        csvwriter.writerow(
            ['Organization', 'Repo', 'Name', 'Username', 'Email', 'Type interaction'])
        for org in orgs:
            org_name = org.name
            org_login = org.login
            print("~~~~~~~~~~~~~~~~~~~~~~~~~~~ ", org_name, " ~~~~~~~~~~~~~~~~~~~~~~~~~~~\n")
            repos = org.get_repos()
            for i, repo in enumerate(repos):
                if repo.fork == False:
                    repo_name = repo.name
                    print("\nCollecting e-mails for", repo_name)
                    count = 0
                    try:
                        stats = repo.get_stats_contributors()
                        for stat in stats:
                            commiter_login = str(stat.author)
                            commiter_login = (commiter_login.replace('NamedUser(login="', "")).replace('")', "")
                            if commiter_login not in members_list:
                                r = s.get("https://api.github.com/users/" + commiter_login)
                                r_user = json.loads(r.text)
                                commiter_email = r_user['email']
                                commiter_name = r_user['name']
                                if commiter_email != None:
                                    count += 1
                                    print(commiter_email)
                                    csvwriter.writerow(
                                        [org_login, repo_name, commiter_name, commiter_login, commiter_email,
                                         "commit"])
                    except TypeError:
                        print("type error, skipping")
                        next
                    print(" -----", str(count), "emails collected")


currenttoken = input("Type your Github token: ")

remaining_limit = get_rate_limit(currenttoken)

if remaining_limit > 0:
    members_login, members_name = list_org_members("src-d", currenttoken)
    users_forked = get_users_forked(members_login, currenttoken)
    users_starred = get_users_starred(members_login, currenttoken)
    users_commited = get_users_comitted(members_login, currenttoken)
elif remaining_limit == 0:
    print("rate limit exceeded")