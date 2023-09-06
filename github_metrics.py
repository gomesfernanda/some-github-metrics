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

def export_repo_metrics(directory,organization, authToken):
    g = Github(authToken)
    dt_today = datetime.datetime.now()
    today = dt_today.date()
    today = str(today).replace("-", "")
    
    totalrepos = 0
    allorgs = g.get_user().get_orgs()

    with open(directory + "/github_repo_metrics_" + organization + "_" + today+ ".csv", 'w', encoding='utf-8') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',')
        csvwriter.writerow(
            ["date", "org", "repo", "open prs", "pr avg age", "pr max age", "newest pr created", "closed prs", "avg time to close", 
            "pr \% in org", "pr \% non org", "pr \% bot",
            "open issues", "issue avg age", "issue max age", "newest issue opened", "issue \% in org", "issue \% non org", "issue \% bot"])
        for orgs in allorgs:
            if orgs.login == organization:
                print("Gathering repository metrics for", orgs.login)
                members = orgs.get_members()
                for repo in orgs.get_repos():
                    if not repo.archived:
                        pr_open_count = 0
                        pr_max_open = 0
                        pr_max_date = datetime.datetime.min
                        pr_open_total_days = 0
                        pr_closed_count = 0
                        pr_closed_total_days = 0
                        pr_in_org = 0
                        pr_non_org = 0
                        pr_bot = 0
                        pulls = repo.get_pulls(state='all', sort='created')
                        for pr in pulls:
                            owner = pr.user
                            if owner.login and "bot" in owner.login.lower():
                                pr_bot += 1
                            elif owner in members:
                                pr_in_org += 1
                            else:
                                pr_non_org += 1

                            if pr.created_at > pr_max_date:
                                    pr_max_date = pr.created_at

                            if pr.state == 'open':
                                pr_open_count += 1

                                days_open = (dt_today - pr.created_at).days
                                pr_open_total_days += days_open
                                if days_open > pr_max_open:
                                    pr_max_open = days_open
                                
                            else:
                                pr_closed_count += 1

                                closed = pr.closed_at if pr.closed_at else datetime.datetime.min
                                merged = pr.merged_at if pr.merged_at else datetime.datetime.min
                                end_date = max(closed, merged)
                                days_open = (end_date- pr.created_at).days
                                pr_closed_total_days += days_open
                                if days_open > pr_max_open:
                                    pr_max_open = days_open

                        print(f"{repo.name} - {pulls.totalCount} - {pr_open_count}")

                        pr_avg_open = f"{pr_open_total_days/pr_open_count:.2f}" if pr_open_count > 0 else 0
                        pr_avg_close_time = f"{pr_closed_total_days/pr_closed_count:.2f}" if pr_closed_count > 0 else 0
                        pr_pct_org = f"{(pr_in_org/(pr_open_count + pr_closed_count)) * 100:.2f}" if pr_closed_count + pr_open_count > 0 else 0
                        pr_pct_non_org = f"{(pr_non_org/(pr_open_count + pr_closed_count)) * 100:.2f}" if pr_closed_count + pr_open_count > 0 else 0
                        pr_pct_bot = f"{(pr_bot/(pr_open_count + pr_closed_count)) * 100:.2f}" if pr_closed_count + pr_open_count > 0 else 0
                        pr_display_date = pr_max_date.date() if pr_max_date != datetime.datetime.min else "N/A"
                        
                        i_open_count = 0
                        i_max_open = 0
                        i_max_date = datetime.datetime.min
                        i_open_total_days = 0
                        i_closed_count = 0
                        i_closed_total_days = 0
                        i_in_org = 0
                        i_non_org = 0
                        i_bot = 0
                        for iss in repo.get_issues(state='all', sort='created'):
                            owner = iss.user
                            if owner.login and "bot" in owner.login.lower():
                                i_bot += 1
                            elif owner in members:
                                i_in_org += 1
                            else:
                                i_non_org += 1

                            if iss.created_at > i_max_date:
                                i_max_date = iss.created_at

                            if iss.state == 'open':
                                i_open_count += 1

                                # print(f'{pr.created_at}')
                                days_open = (dt_today - iss.created_at).days
                                i_open_total_days += days_open
                                if days_open > i_max_open:
                                    i_max_open = days_open
                                
                            else:
                                i_closed_count += 1

                                days_open = (iss.closed_at- iss.created_at).days
                                i_closed_total_days += days_open
                                # if days_open > pr_max_open:
                                #     pr_max_open = days_open
                                # if pr.created_at > pr_max_date:
                                #     pr_max_date = pr.created_at

                        i_avg_open = f"{i_open_total_days/i_open_count:.2f}" if i_open_count > 0 else 0
                        i_avg_close_time = f"{i_closed_total_days/i_closed_count:.2f}" if i_closed_count > 0 else 0
                        i_pct_org = f"{(i_in_org/(i_open_count + i_closed_count)) * 100:.2f}" if i_closed_count + i_open_count > 0 else 0
                        i_pct_non_org = f"{(i_non_org/(i_open_count + i_closed_count)) * 100:.2f}" if i_closed_count + i_open_count > 0 else 0
                        i_pct_bot = f"{(i_bot/(i_open_count + i_closed_count)) * 100:.2f}" if i_closed_count + i_open_count > 0 else 0
                        i_display_date = i_max_date.date() if i_max_date != datetime.datetime.min else "N/A"

                        csvwriter.writerow(
                            [todaystr, organization, repo.name, pr_open_count, pr_avg_open, pr_max_open, pr_display_date,
                            pr_closed_count, pr_avg_close_time, pr_pct_org, pr_pct_non_org, pr_pct_bot, i_open_count, 
                            i_avg_open, i_max_open, i_display_date, i_pct_org, i_pct_non_org, i_pct_bot])

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
        print("")
        list_org_members(organization, authToken)
        print("")
        export_code_frequency(directory, organization, authToken)
        print("")
        export_community_engagement(directory, organization, authToken)
        print("")
        export_repo_metrics(directory, organization, authToken)
    except Exception as e:
        print(e)


if __name__ == '__main__':
    main()