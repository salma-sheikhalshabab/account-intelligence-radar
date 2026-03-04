import urllib.robotparser
from urllib.parse import urlparse


def is_linkedin(url: str) -> bool:
    return "linkedin.com" in url.lower()


def is_allowed_by_robots(url: str, user_agent: str = "*") -> bool:
    try:
        parsed = urlparse(url)
        robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"

        rp = urllib.robotparser.RobotFileParser()
        rp.set_url(robots_url)
        rp.read()

        return rp.can_fetch(user_agent, url)

    except Exception:
        # If robots.txt is unreachable or unreadable, assume allowed.
        # Only block URLs that explicitly disallow crawling.
        return True


def filter_allowed_urls(urls: list) -> list:

    allowed_urls = []

    for url in urls:

        # Block LinkedIn — explicitly prohibited by their ToS
        if is_linkedin(url):
            print(f"⚠ Skipping LinkedIn URL: {url}")
            continue

        if is_allowed_by_robots(url):
            allowed_urls.append(url)
        else:
            print(f"⚠ Blocked by robots.txt: {url}")

    return allowed_urls