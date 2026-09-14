import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

_session = None


def get_session():
    global _session
    if _session is not None:
        return _session
    s = requests.Session()
    retry = Retry(
        total=1,
        backoff_factor=0.2,
        status_forcelist=[429, 500, 502, 503],
        allowed_methods=["GET", "POST"],
        respect_retry_after_header=True,
    )
    adapter = HTTPAdapter(pool_connections=20, pool_maxsize=20, max_retries=retry)
    s.mount("https://", adapter)
    s.mount("http://", adapter)
    s.headers.update({"Accept": "application/json", "User-Agent": "MusicPlatform/1.0"})
    _session = s
    return _session
