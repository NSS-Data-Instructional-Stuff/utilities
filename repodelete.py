#!/usr/bin/env python
# thank you Andy
import requests
import getpass
import configparser

GITHUB_GET_REPOS_API = "https://api.github.com/orgs/{}/repos"
GITHUB_REPO_API = "https://api.github.com/repos/{}"
CONFIG_FILE = "config.ini"


def get_all_repos(org, token):
    return requests.get(GITHUB_GET_REPOS_API.format(org), headers=headers(token)).json()


def delete_repo(repo_name, token):
    res = requests.delete(GITHUB_REPO_API.format(repo_name), headers=headers(token))
    if res.status_code < 200 or res.status_code > 300:
        print(f"ERROR: Delete failed for {repo_name}")
        print(res.json())
        raise Exception(f"ERROR: Delete failed for {repo_name}")


def delete_repos(repo_names, token):
    for repo_name in repo_names:
        print(f"Deleting {repo_name}...")
        delete_repo(repo_name, token)


def headers(token):
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.inertia-preview+json",
        "User-Agent": "repodelete",
    }


def diff_lists(list1, list2):
    upper_list2 = [el.upper() for el in list2]
    return [el for el in list1 if el.upper() not in upper_list2]


def prompt_for_org_info():
    org = input("Github Org: ")
    while not org:
        org = input("Github Org: ")

    return org.strip()


def load_token():
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)
    try:
        token = config["Github"]["PersonalAccessToken"].strip()
        if token == "":
            raise ValueError()
        print(f"Found Github Personal Access Token in {CONFIG_FILE}")
        return token
    except:
        print("ERROR: Unable to load Github Personal Access Token from {CONFIG_FILE}")
        raise


def prompt_for_repos_to_keep():
    print("Enter the repos to keep. (one per line, enter a blank line when done)")

    repos_to_keep = []
    repo = input()
    while repo.strip():
        repos_to_keep.append(repo)
        repo = input()

    return repos_to_keep


if __name__ == "__main__":
    org = prompt_for_org_info()
    token = load_token()

    repos = get_all_repos(org, token)
    full_names = [repo["full_name"] for repo in repos]

    print("Found the following repos:")
    print("\n".join(full_names))

    keep_names = [
        f"{org}/{name}" if "/" not in name else name
        for name in prompt_for_repos_to_keep()
    ]

    delete_names = diff_lists(full_names, keep_names)

    print("The following repos will be PERMENANTLY deleted.")
    print("\n".join(delete_names))
    confirm = input("Do you wish to proceed? (yes/no)")
    if confirm != "yes":
        print("...probably a wise choice.")
    else:
        delete_repos(delete_names, token)
