import argparse
import requests
import json
from github import Github
import csv
from datetime import date, timedelta

end_date = date.today() - timedelta(days=1)
start_date = end_date - timedelta(days=14)

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
                if repo.fork == False and repo.private == False:
                    currentrepo = repo.name
                    r = s.get("https://api.github.com/repos/" + organization + "/" + currentrepo + "/traffic/views")
                    r_views = json.loads(r.text)
                    try:
                        if r_views["message"] == "Must have push access to repository":
                            repos_noaccess.append(currentrepo)
                    except:
                        repos_ok.append(currentrepo)
    return repos_noaccess, repos_ok

def export_traffic(organization, authtoken):
    count=0
    s = requests.Session()
    s.headers.update({'Authorization': 'token ' + authtoken})
    g = Github(authtoken)
    repos_noaccess, repos_ok = test_push_access(organization, authtoken)
    with open("github_views_" + organization + ".csv", 'w', encoding='utf-8') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',')
        csvwriter.writerow(
            ["repo", "date", "views count", "views uniques"])
        reposlist = []
        allrepos = g.get_user().get_repos()
        print("Collecting traffic data from", organization, "repositories. \n")
        for repo in allrepos:
            repo_owner = str(repo.owner)
            repo_owner = (repo_owner.replace('NamedUser(login="', "")).replace('")', "")
            if repo.fork == False and repo.private == False and repo_owner == organization and repo.name in repos_ok:
                reposlist.append(repo.name)
        print("\n======================= VIEWS =======================")
        for i in reposlist:
            count+=1
            print("[", count, "/", len(repos_ok), "] - views for", i)
            r_views = s.get("https://api.github.com/repos/" + organization + "/" + i + "/traffic/views")
            r_views = json.loads(r_views.text)
            for date in r_views["views"]:
                fixeddate = str(date["timestamp"]).replace("T00:00:00Z", "")
                csvwriter.writerow(
                    [i, fixeddate, date["count"], date["uniques"]])
    count=0
    with open("github_clones_" + organization + ".csv", 'w', encoding='utf-8') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',')
        csvwriter.writerow(
            ["repo", "date", "clones count", "clones uniques"])
        print("\n======================= CLONES ======================")
        for i in reposlist:
            count += 1
            print("[", count, "/", len(repos_ok), "] - clones for", i)
            r_clones = s.get("https://api.github.com/repos/" + organization + "/" + i + "/traffic/clones")
            r_clones = json.loads(r_clones.text)
            for date in r_clones["clones"]:
                fixeddate = str(date["timestamp"]).replace("T00:00:00Z","")
                #fixeddate = fixeddate.replace("T00:00:00Z","")
                csvwriter.writerow(
                    [i, fixeddate, date["count"], date["uniques"]])
    count=0
    with open("github_paths_" + organization + ".csv", 'w', encoding='utf-8') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',')
        csvwriter.writerow(
            ["start date", "end date", "repo", "path", "title", "count", "uniques"])
        print("\n======================= PATHS =======================")
        for i in reposlist:
            count +=1
            print("[", count, "/", len(repos_ok), "] - paths for", i)
            r_paths = s.get("https://api.github.com/repos/" + organization + "/" + i + "/traffic/popular/paths")
            r_paths = json.loads(r_paths.text)
            for path in r_paths:
                csvwriter.writerow(
                    [start_date, end_date, i, path["path"], path["title"], path["count"], path["uniques"]])
    count=0
    with open("github_referrers_" + organization + ".csv", 'w', encoding='utf-8') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',')
        csvwriter.writerow(
            ["start date", "end date", "repo", "referrer", "count", "uniques"])
        print("\n======================= REFERRERS ===================")
        for i in reposlist:
            count+=1
            print("[", count, "/", len(repos_ok), "] - referrers for", i)
            r_referrers = s.get("https://api.github.com/repos/" + organization + "/" + i + "/traffic/popular/referrers")
            r_referrers = json.loads(r_referrers.text)
            for reff in r_referrers:
                csvwriter.writerow(
                    [start_date, end_date, i, reff["referrer"], reff["count"], reff["uniques"]])

def main():
    args = setup()
    organization = args.org
    authToken = args.token
    s = requests.Session()
    s.headers.update({'Authorization': 'token ' + authToken})
    g = Github(authToken)
    try:
        ratelimit = g.rate_limiting
        print("Valid token. Starting process. \n")
        repos_noaccess, repos_ok = test_push_access(organization, authToken)
        print("Repos without push access: ", repos_noaccess, "\n")
        print("Repos ok: ", repos_ok, "\n")
        print("")
        export_traffic(organization, authToken)
    except:
        print("Could not complete tasks.")



if __name__ == '__main__':
    main()