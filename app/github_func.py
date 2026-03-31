import requests

GITHUB_API = "https://api.github.com/repos"

def parse_repo(url: str):
    """
    Extracts owner and repository name from a GitHub URL.
    """
    parts = url.rstrip("/").split("/")
    if len(parts) < 2:
        raise ValueError("Invalid GitHub URL")

    owner = parts[-2]
    repo = parts[-1]
    return owner, repo


def get_repo_tree(owner, repo):
    """
    Fetches the repository tree from GitHub API, returning a list of files with their paths and types.
    """
    url = f"{GITHUB_API}/{owner}/{repo}/git/trees/HEAD?recursive=1"
    r = requests.get(url)
    r.raise_for_status()
    return r.json()["tree"]


def download_file(owner, repo, path):
    """
    Downloads the content of a file from the GitHub repository using the raw URL format.
    """
    raw = f"https://raw.githubusercontent.com/{owner}/{repo}/HEAD/{path}"
    r = requests.get(raw)
    if r.status_code != 200:
        return None
    return r.text
