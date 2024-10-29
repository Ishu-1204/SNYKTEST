import requests
from datetime import datetime, timedelta
from prettytable import PrettyTable

def make_http_request(url, method='GET', data=None):
    """
    Makes an HTTP request to the given URL with the specified method and data.
    
    Args:
        url (str): The URL to make the request to.
        method (str): The HTTP method to use ('GET' or 'PATCH'). Defaults to 'GET'.
        data (dict): The data to send with the request (for 'PATCH' method). Defaults to None.
    
    Returns:
        response (requests.Response): The response object from the request.
    """
    token = "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"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    try:
        if method == 'GET':
            response = requests.get(url, headers=headers)
        elif method == 'PATCH':
            response = requests.patch(url, headers=headers, json=data)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        print(f"HTTP request failed: {e}")
        return None

def fetch_repositories(org_name):
    """
    Fetches the list of repositories for the given organization.
    
    Args:
        org_name (str): The name of the organization.
    
    Returns:
        list: A list of repositories.
    """
    url = f"https://api.github.com/orgs/{org_name}/repos"
    response = make_http_request(url)
    if response and response.status_code == 200:
        return response.json()
    else:
        print("Failed to fetch repositories")
        return []

def filter_old_repositories(repos):
    """
    Filters repositories that have not been updated in the last 90 days.
    
    Args:
        repos (list): A list of repositories.
    
    Returns:
        list: A list of old repositories.
    """
    three_months_ago = datetime.now() - timedelta(days=90)
    old_repos = [repo for repo in repos if datetime.strptime(repo['updated_at'], '%Y-%m-%dT%H:%M:%SZ') < three_months_ago]
    return old_repos

def fetch_access_control(repo):
    """
    Fetches the access control details (collaborators and teams) for the given repository.
    
    Args:
        repo (dict): The repository details.
    
    Returns:
        dict: A dictionary containing collaborators and teams.
    """
    collaborators_url = repo['url'] + "/collaborators"
    teams_url = repo['url'] + "/teams"
    
    collaborators_response = make_http_request(collaborators_url)
    teams_response = make_http_request(teams_url)
    
    access_control = {
        "collaborators": collaborators_response.json() if collaborators_response and collaborators_response.status_code == 200 else [],
        "teams": teams_response.json() if teams_response and teams_response.status_code == 200 else []
    }
    
    return access_control

def fetch_org_members(org_name):
    """
    Fetches the list of members for the given organization.
    
    Args:
        org_name (str): The name of the organization.
    
    Returns:
        list: A list of organization members.
    """
    url = f"https://api.github.com/orgs/{org_name}/members"
    response = make_http_request(url)
    if response and response.status_code == 200:
        return response.json()
    else:
        print("Failed to fetch organization members")
        return []

def archive_repository(repo):
    """
    Archives the given repository.
    
    Args:
        repo (dict): The repository details.
    
    Returns:
        None
    """
    url = repo['url']
    data = {"archived": True}
    response = make_http_request(url, method='PATCH', data=data)
    if response and response.status_code == 200:
        print(f"Successfully archived repository: {repo['name']}")
    else:
        print(f"Failed to archive repository: {repo['name']}")

def main():
    """
    Main function to fetch repositories, filter old ones, fetch access control details,
    and archive old repositories.
    
    Returns:
        None
    """
    org_name = "Ishu-1204"
    
    repos = fetch_repositories(org_name)
    print(f"Total repositories: {len(repos)}")
   
    org_members = fetch_org_members(org_name)
    print(f"Total organization members: {len(org_members)}")

    table = PrettyTable(["Collaborator", "Permissions", "Designation"])
    
    for repo in repos:
        access_control = fetch_access_control(repo)
        print(f"*************************************************************")

        print(f"Repository: {repo['name']}")
        print(f"  - Type: {'Private' if repo['private'] else 'Public'}")
        print(f"###########################################################")
        print("  - Collaborators:")
        print(f"###########################################################")
        for collaborator in access_control['collaborators']:
            permissions = collaborator['permissions']
            designation = ""

            # Admin check
            if all(permissions.values()):
                designation = "admin"
            # Read-only check
            elif permissions.get('pull', False) and not any(v for k, v in permissions.items() if k != 'pull'):
                designation = "read only"
            # Write-only check
            elif permissions.get('push', False) and not any(v for k, v in permissions.items() if k != 'push'):
                designation = "write only"
            # Maintain-only check
            elif permissions.get('maintain', False) and not any(v for k, v in permissions.items() if k != 'maintain'):
                designation = "maintain only"
        
            table.add_row([collaborator['login'], permissions, designation])

        print(table)
        print("  - Teams:")
        for team in access_control['teams']:
            print(f"    - {team['name']} (Permission: {team['permission']})")
        print(f"###########################################################")
        print("  - Organization Members:")
        for member in org_members:
            print(f"    - {member['login']}")
            
    print(f"###########################################################")

    old_repos = filter_old_repositories(repos)
    print(f"Old repositories: {len(old_repos)}")
    
    if not old_repos:
        print("No old repositories to archive.")
    else: 
        for repo in old_repos:
            archive_repository(repo)

if __name__ == "__main__":
    main()
