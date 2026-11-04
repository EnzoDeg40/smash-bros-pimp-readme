import json
import os
import re
import urllib.request

COMMIT_SUBJECT = "Update README with character renders"


def fetch_github_user(login: str) -> dict | None:
    if not re.fullmatch(r"[A-Za-z0-9-]+", login):
        print(f"⚠️  Invalid GitHub username: {login!r}")
        return None

    headers = {"User-Agent": "smash-bros-pimp-readme"}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    request = urllib.request.Request(
        f"https://api.github.com/users/{login}", headers=headers
    )
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            return json.load(response)
    except (OSError, ValueError) as e:
        # a missing co-author must not prevent the README update
        print(f"⚠️  Unable to find GitHub user {login}: {e}")
        return None


def coauthor_trailer(user: dict) -> str:
    # GitHub links the co-author to the account through this noreply address
    login = user["login"]
    return f"Co-authored-by: {login} <{user['id']}+{login}@users.noreply.github.com>"


def build_commit_message(logins: list[str]) -> str:
    unique_logins = {login.lower(): login for login in logins}.values()
    users = [fetch_github_user(login) for login in unique_logins]
    trailers = [coauthor_trailer(user) for user in users if user]

    if not trailers:
        return f"{COMMIT_SUBJECT}\n"

    return f"{COMMIT_SUBJECT}\n\n" + "\n".join(trailers) + "\n"
