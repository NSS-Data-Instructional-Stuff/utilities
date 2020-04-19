#!/usr/bin/env python
# thank you Andy
import requests
import getpass

GITHUB_GET_REPOS_API = 'https://api.github.com/orgs/{}/repos'
GITHUB_REPO_API = 'https://api.github.com/repos/{}'


def get_all_repos(org, username, password):
    return requests.get(GITHUB_GET_REPOS_API.format(org), auth=(username, password)).json()


def delete_repo(repo_name, username, password):
    requests.delete(GITHUB_REPO_API.format(repo_name), auth=(username, password))


def delete_repos(repo_names, username, password):
    for repo_name in repo_names:
        print(f'Deleting {repo_name}...')
        delete_repo(repo_name, username, password)


def diff_lists(list1, list2):
    upper_list2 = [ el.upper() for el in list2 ]
    return [ el for el in list1 if el.upper() not in upper_list2 ]


def prompt_for_user_info():
    org = input('Github Org: ')
    username = input('Github Username: ')
    password = getpass.getpass('Github Password: ')
    return (org, username, password)


def prompt_for_repos_to_keep():
    print('Enter the repos to keep. (one per line, enter a blank line when done)')

    repos_to_keep = []
    repo = input()
    while repo.strip():
        repos_to_keep.append(repo)
        repo = input()

    return repos_to_keep


if __name__ == '__main__':
    org, username, password = prompt_for_user_info()

    repos = get_all_repos(org, username, password)
    #print(repos)
    full_names = [ repo['full_name'] for repo in repos ]

    print('Found the following repos:')
    print('\n'.join(full_names))

    keep_names = [ f'{org}/{name}' if '/' not in name else name
                   for name in prompt_for_repos_to_keep() ]

    delete_names = diff_lists(full_names, keep_names)

    print('The following repos will be PERMENANTLY deleted.')
    print('\n'.join(delete_names))
    confirm = input('Do you wish to proceed? (yes/no)')
    if confirm != 'yes':
        print('...probably a wise choice.')
    else:
        delete_repos(delete_names, username, password)
