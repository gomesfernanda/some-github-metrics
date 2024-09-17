import argparse
import requests
import json
from github import Github
import csv
from datetime import date, timedelta
import os
import numpy as np
import pandas as pd


end_date = date.today() - timedelta(days=1)
start_date = end_date - timedelta(days=14)
today = str(date.today())
today = today.replace("-", "")

def setup():
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--org", help="choose what company you what to see", required=True)
    parser.add_argument("-t", "--token", help="OAuth token from GitHub", required=True)
    args = parser.parse_args()
    return args

def test_push_access(organization, authToken):
    s = requests.Session()
    s.headers.update({'Authorization': 'token ' + authToken})
    g = Github(authToken)
    repos_ok = []
    repos_noaccess = []
    allorgs = g.get_user().get_orgs()
    for orgs in allorgs:
        if orgs.login == organization:
            print("Checking push access for", orgs.name, "repositories. \n")
            for repo in orgs.get_repos():
                if repo.fork == False and repo.archived == False:
                    currentrepo = repo.name
                    r = s.get("https://api.github.com/repos/" + organization + "/" + currentrepo + "/traffic/views")
                    r_views = json.loads(r.text)
                    try:
                        if r_views["message"] == "Must have push access to repository":
                            repos_noaccess.append(currentrepo)
                    except:
                        repos_ok.append(currentrepo)
    return repos_noaccess, repos_ok


def relevantrepos_noaccess(numstars, repos_noaccess, organization, authToken):
    g = Github(authToken)
    repos_dict = {}
    allorgs = g.get_user().get_orgs()
    for orgs in allorgs:
        if orgs.login == organization:
            for repo in orgs.get_repos():
                reponame = repo.name
                stars = repo.stargazers_count
                if reponame in repos_noaccess and stars >= numstars:
                    repos_dict[reponame] = stars
    return repos_dict


def export_traffic(directory, organization, repos_ok, authtoken):
    s = requests.Session()
    s.headers.update({'Authorization': 'token ' + authtoken})
    g = Github(authtoken)
    reposlist = []
    allrepos = g.get_user().get_repos()

    print("Collecting traffic data from", organization, "repositories. \n")

    for repo in allrepos:
        repo_owner = str(repo.owner)
        repo_owner = (repo_owner.replace('NamedUser(login="', "")).replace('")', "")
        if repo.fork == False and repo.archived == False and repo_owner == organization and repo.name in repos_ok:
            reposlist.append(repo.name)

    count=0
    countrow = 0
    views_array = np.zeros(((len(repos_ok) * 15), 5), dtype=np.object_)
    views_array[0, 0] = "Org"
    views_array[0, 1] = "Repo"
    views_array[0, 2] = "Date"
    views_array[0, 3] = "Views count"
    views_array[0, 4] = "Views unique"
    print("\n======================= VIEWS =======================")
    for i in reposlist:
        count+=1
        print("[", str(count).zfill(2), "|", len(repos_ok), "] views for", i)
        r_views = s.get("https://api.github.com/repos/" + organization + "/" + i + "/traffic/views")
        r_views = json.loads(r_views.text)
        for date in r_views["views"]:
            countrow += 1
            fixeddate = str(date["timestamp"]).replace("T00:00:00Z", "")
            views_array[countrow, 0] = organization
            views_array[countrow, 1] = i
            views_array[countrow, 2] = fixeddate
            views_array[countrow, 3] = date["count"]
            views_array[countrow, 4] = date["uniques"]
    df = pd.DataFrame(views_array[1:], columns=views_array[0])
    df = df[(df.T != 0).any()]
    df['Date'] = pd.to_datetime(df.Date)
    sorteddf = df.sort_values(['Date', 'Repo'])
    sorteddf.to_csv(directory + "/github_views_" + organization + "_" + today + ".csv", sep=',', encoding='utf-8', index=False)

    count=0
    countrow = 0
    clones_array = np.zeros(((len(repos_ok) * 15), 5), dtype=np.object_)
    clones_array[0, 0] = "Org"
    clones_array[0, 1] = "Repo"
    clones_array[0, 2] = "Date"
    clones_array[0, 3] = "Clones count"
    clones_array[0, 4] = "Clones unique"
    print("\n======================= CLONES ======================")
    for i in reposlist:
        count += 1
        print("[", str(count).zfill(2), "|", len(repos_ok), "] clones for", i)
        r_clones = s.get("https://api.github.com/repos/" + organization + "/" + i + "/traffic/clones")
        r_clones = json.loads(r_clones.text)
        for date in r_clones["clones"]:
            countrow += 1
            fixeddate = str(date["timestamp"]).replace("T00:00:00Z", "")
            clones_array[countrow, 0] = organization
            clones_array[countrow, 1] = i
            clones_array[countrow, 2] = fixeddate
            clones_array[countrow, 3] = date["count"]
            clones_array[countrow, 4] = date["uniques"]
    df = pd.DataFrame(clones_array[1:], columns=clones_array[0])
    df = df[(df.T != 0).any()]
    df['Date'] = pd.to_datetime(df.Date)
    sorteddf = df.sort_values(['Date', 'Repo'])
    sorteddf.to_csv(directory + "/github_clones_" + organization + "_" + today + ".csv", sep=',', encoding='utf-8', index=False)


    count=0
    countrow = 0
    paths_array = np.zeros(((len(repos_ok) * 10), 8), dtype=np.object_)
    paths_array[0, 0] = "Start date"
    paths_array[0, 1] = "End date"
    paths_array[0, 2] = "Org"
    paths_array[0, 3] = "Repo"
    paths_array[0, 4] = "Path"
    paths_array[0, 5] = "Title"
    paths_array[0, 6] = "Count"
    paths_array[0, 7] = "Unique"
    with open(directory + "/github_paths_" + organization + "_" + today + ".csv", 'w', encoding='utf-8') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',')
        csvwriter.writerow(
            ["start date", "end date", "repo", "path", "title", "count", "uniques"])
    print("\n======================= PATHS =======================")
    for i in reposlist:
        count +=1
        print("[", str(count).zfill(2), "|", len(repos_ok), "] paths for", i)
        r_paths = s.get("https://api.github.com/repos/" + organization + "/" + i + "/traffic/popular/paths")
        r_paths = json.loads(r_paths.text)
        for path in r_paths:
            countrow += 1
            paths_array[countrow, 0] = start_date
            paths_array[countrow, 1] = end_date
            paths_array[countrow, 2] = organization
            paths_array[countrow, 3] = i
            paths_array[countrow, 4] = path["path"]
            paths_array[countrow, 5] = path["title"]
            paths_array[countrow, 6] = path["count"]
            paths_array[countrow, 7] = path["uniques"]
    df = pd.DataFrame(paths_array[1:], columns=paths_array[0])
    df = df[(df.T != 0).any()]
    df.to_csv(directory + "/github_paths_" + organization + "_" + today + ".csv", sep=',', encoding='utf-8', index=False)


    count=0
    countrow = 0
    referrers_array = np.zeros(((len(repos_ok) * 10), 7), dtype=np.object_)
    referrers_array[0, 0] = "Start date"
    referrers_array[0, 1] = "End date"
    referrers_array[0, 2] = "Org"
    referrers_array[0, 3] = "Repo"
    referrers_array[0, 4] = "Referrer"
    referrers_array[0, 5] = "Count"
    referrers_array[0, 6] = "Unique"
    print("\n======================= REFERRERS ===================")
    for i in reposlist:
        count+=1
        print("[", str(count).zfill(2), "|", len(repos_ok), "] referrers for", i)
        r_referrers = s.get("https://api.github.com/repos/" + organization + "/" + i + "/traffic/popular/referrers")
        r_referrers = json.loads(r_referrers.text)
        for reff in r_referrers:
            countrow += 1
            referrers_array[countrow, 0] = start_date
            referrers_array[countrow, 1] = end_date
            referrers_array[countrow, 2] = organization
            referrers_array[countrow, 3] = i
            referrers_array[countrow, 4] = reff["referrer"]
            referrers_array[countrow, 5] = reff["count"]
            referrers_array[countrow, 6] = reff["uniques"]
    df = pd.DataFrame(referrers_array[1:], columns=referrers_array[0])
    df = df[(df.T != 0).any()]
    df.to_csv(directory + "/github_referrers_" + organization + "_" + today + ".csv", sep=',', encoding='utf-8', index=False)

def main():
    args = setup()
    organization = args.org
    authToken = args.token
    s = requests.Session()
    s.headers.update({'Authorization': 'token ' + authToken})
    g = Github(authToken)
    directory = "output/" + organization
    if not os.path.exists(directory):
        os.makedirs(directory)
    try:
        ratelimit = g.rate_limiting
        print("Valid token. Starting process. \n")
        repos_noaccess, repos_ok = test_push_access(organization, authToken)
        print("Repos without push access: ", repos_noaccess, "\n")
        print("Repos ok: ", repos_ok, "\n")
        print("")
        export_traffic(directory, organization, repos_ok, authToken)
        print("")
        print("Repos with over 25 stars without push access:")
        print(relevantrepos_noaccess(25, repos_noaccess, organization, authToken))

    except:
        print("Could not complete tasks.")



if __name__ == '__main__':
    main()
