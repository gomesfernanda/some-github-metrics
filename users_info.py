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
todaystr = str(today).replace("-", "")


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


def get_users_info(members_list, authToken):
    g = Github(authToken)
    s.headers.update({'Authorization': 'token ' + authToken})
    orgs = g.get_user().get_orgs()
    with open("github_users_info_" + todaystr + ".csv", 'w', encoding='utf-8') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',')
        csvwriter.writerow(
            ['Organization', 'Repo', 'Name', 'Username', 'Email', 'Date interaction', 'Type interaction'])
        for org in orgs:
            org_name = org.name
            org_login = org.login
            print("\n~~~~~~~~~~~~~~~~~~~~~~~~~~~ ", org_name, " ~~~~~~~~~~~~~~~~~~~~~~~~~~~")
            repos = org.get_repos()
            totalrepos = 0
            repocount = 0
            for repo in repos:
                if repo.fork == False:
                    totalrepos += 1
            for i, repo in enumerate(repos):
                if repo.fork == False:
                    repo_name = repo.name
                    repocount += 1
                    print("\n--> Repo [", repocount, "/", totalrepos, "] :", repo_name)
                    count = 0
                    forks = repo.get_forks()
                    for fork in forks:
                        forker_login = fork.owner.login
                        forker_name = fork.owner.name
                        forker_email = fork.owner.email
                        forker_date = fork.created_at
                        forker_date = forker_date.date()
                        if forker_login not in members_list and forker_email != None:
                            count += 1
                            print("fork //", forker_email, "//", forker_date)
                            csvwriter.writerow(
                                [org_login, repo_name, forker_name, forker_login, forker_email, forker_date, "fork"])
                    stargazers = repo.get_stargazers_with_dates()
                    for stargazer in stargazers:
                        stargazer_name = stargazer.user.name
                        stargazer_login = stargazer.user.login
                        stargazer_email = stargazer.user.email
                        stargazer_date = stargazer.starred_at
                        stargazer_date = stargazer_date.date()
                        if stargazer_login not in members_list and stargazer_email != None:
                            count += 1
                            print("star //", stargazer_email, "//", stargazer_date)
                            csvwriter.writerow(
                                [org_login, repo_name, stargazer_name, stargazer_login, stargazer_email, stargazer_date,
                                 "star"])
                    try:
                        stats = repo.get_stats_contributors()
                        for stat in stats:
                            weeks_list = []
                            for week in stat.weeks:
                                if week.c != 0:
                                    weeks_list.append(week.w)
                            commiter_date = weeks_list[-1]
                            commiter_date = commiter_date.date()
                            commiter_login = str(stat.author)
                            commiter_login = (commiter_login.replace('NamedUser(login="', "")).replace('")', "")
                            if commiter_login not in members_list:
                                r = s.get("https://api.github.com/users/" + commiter_login)
                                r_user = json.loads(r.text)
                                commiter_email = r_user['email']
                                commiter_name = r_user['name']
                                if commiter_email != None:
                                    count += 1
                                    print("commit //", commiter_email, "//", commiter_date)
                                    csvwriter.writerow(
                                        [org_login, repo_name, commiter_name, commiter_login, commiter_email,
                                         commiter_date,
                                         "commit"])
                    except TypeError as e:
                        print(e)
                        next


currenttoken = input("Type your Github token: ")

remaining_limit = get_rate_limit(currenttoken)

if remaining_limit > 0:
    members_login, members_name = list_org_members("src-d", currenttoken)
    users_commited = get_users_info(members_login, currenttoken)
elif remaining_limit == 0:
    print("rate limit exceeded")
