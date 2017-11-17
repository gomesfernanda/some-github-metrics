import json
from urllib.request import urlopen, Request
from github import Github
import csv
import ssl

ssl._create_default_https_context = ssl._create_unverified_context


def getOrgs(authToken):
    g = Github(authToken)
    orgslist = []
    for orgs in g.get_user().get_orgs():
        orgslist.append(orgs.login)
    return orgslist


def getOrgMembers(org, authToken):
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
        url_user = "https://api.github.com/users/" + member
        request = Request(url_user)
        request.add_header('Authorization', 'token %s' % authToken)
        response = urlopen(request)
        r_user = json.load(response)
        if r_user["name"] != None:
            namesmembers.append(r_user["name"])
        else:
            namesmembers.append(r_user["login"])
    return loginmembers, namesmembers


def getRepo_CodeFrequency(organization, authToken, notparsedrepo=None):
    g = Github(authToken)
    with open("github_RepoStatsContributions_" + organization + ".csv", 'w', encoding='utf-8') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',')
        csvwriter.writerow(
            ["count", "org", "repo", "week", "additions", "deletions", "commits", "author", "external"])
        loginmembers, namesmembers = getOrgMembers(organization, authToken)
        allorgs = g.get_user().get_orgs()
        for orgs in allorgs:
            if orgs.login == organization:
                count = 0
                for repo in orgs.get_repos():
                    if repo.fork == False and repo.private == False:
                        count += 1
                        print(count, "| ", orgs.login, " | ", repo.name)
                        reponame = repo.name
                        try:
                            for stat in repo.get_stats_contributors():
                                author = str(stat.author)
                                author = (author.replace('NamedUser(login="', "")).replace('")', "")
                                for week in stat.weeks:
                                    date = str(week.w)
                                    date = date[:10]
                                    if author in loginmembers:
                                        print(".", end=" ")
                                        try:
                                            csvwriter.writerow(
                                                [count, orgs.login, reponame, date, week.a, week.d, week.c, author,
                                                 "yes"])
                                        except:
                                            print("error")
                                    else:
                                        print(".", end=" ")
                                        try:
                                            csvwriter.writerow(
                                                [count, orgs.login, reponame, date, week.a, week.d, week.c, author,
                                                 "no"])
                                        except:
                                            print("error2")
                            print("")
                        except:
                            print("none")
                            csvwriter.writerow([count, orgs.login, reponame, 0, 0, 0, 0, 0, "n/a"])
            else:
                next


def getRepo_Community(organization, authToken):
    g = Github(authToken)
    with open("github_BasicInfo_" + organization + ".csv", 'w', encoding='utf-8') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',')
        csvwriter.writerow(
            ["count", "org", "repo", "forks", "stars", "commits", "collaborators", "description"])
        allorgs = g.get_user().get_orgs()
        for orgs in allorgs:
            if orgs.login == organization:
                print("Gathering community metrics for", orgs.name, "\n")
                count = 0
                for repo in orgs.get_repos():
                    countcommit = 0
                    countcollab = 0
                    if repo.fork == False and repo.private == False:
                        count += 1
                        for commits in repo.get_commits():
                            countcommit += 1
                        for collab in repo.get_contributors():
                            countcollab += 1
                        print("[", count, "]", repo.name, "|", countcommit, "commits |", repo.forks_count, "forks |",
                              repo.stargazers_count, "stars |", countcollab, "contributors|", repo.description)
                        csvwriter.writerow(
                            [count, organization, repo.name, repo.forks_count, repo.stargazers_count, countcommit,
                             countcollab, repo.description])


# def uniqueCollabs(organization, authToken):
#     g = Github(authToken)
#     with open(csv_uniquecollabs, "w", encoding="utf-8") as csvfile:
#         csvwriter = csv.writer(csvfile, delimiter=',')
#         csvwriter.writerow(["name", "login", "is a member of the organization?"])
#         loginmembers, namesmembers = getOrgMembers(organization, authToken)
#         nameslist = []
#         company = g.get_user().company
#         company = company.strip("@")
#         company = company.strip(" ")
#         for repo in g.get_user().get_repos():
#             count = 0
#             if repo.fork == False and repo.private == False and repo.full_name[:len(company)] == company:
#                 for commit in repo.get_commits():
#                     count += 1
#                     try:
#                         author = commit.author
#                         name = commit.author.name
#                         if name not in nameslist:
#                             author = str(author)
#                             nameslist.append(name)
#                             author = author.replace('")', '')
#                             author = author.replace('NamedUser(login="', '')
#                             if author not in loginmembers:
#                                 csvwriter.writerow([name, author, "no"])
#                                 print(name, "|", author, "| no")
#                             else:
#                                 csvwriter.writerow([name, author, "yes"])
#                                 print(name, "|", author, "| yes")
#                     except:
#                         count += 1


currenttoken = input("\n[STEP 1] Please provide personal access token --> ")

orgs_list = getOrgs(currenttoken)

print("\n[STEP 2] Select the organization you want to analyse:")
for i in range(0, len(orgs_list)):
    print("[", i, "] ", orgs_list[i])

selectednumber = input(" ")

try:
    currentorg = orgs_list[int(selectednumber)]
    print("You chose:", currentorg, "\n")
    print("[STEP 3]")
    members_Yn = input("Do you want to see the members of this organization? [Y/n]: ")
    codefreq_Yn = input("Do you want to export code frequency for all repos? [Y/n]: ")
    community_Yn = input("Do you want to export community metrics for all repos? [Y/n]: ")
    print("\n======================= Starting process =======================\n")
    if members_Yn == "Y" or members_Yn == "y":
        print(getOrgMembers(currentorg, currenttoken))
        print("")
    if codefreq_Yn == "Y" or codefreq_Yn == "y":
        getRepo_CodeFrequency(currentorg, currenttoken)
        print("")
    if community_Yn == "Y" or community_Yn == "y":
        getRepo_Community(currentorg, currenttoken)
    print("\n======================= End of process =======================\n")
except:
    print("Sorry, option not available")