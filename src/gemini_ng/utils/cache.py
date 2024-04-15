import os
from pathlib import Path

from diskcache import Cache

_CACHE = None


def get_cache_dir() -> Path:
    cache_dir = os.environ.get("GEMINI_NG_CACHE_DIR", None)
    if cache_dir is None:
        cache_dir = Path.home() / ".cache" / "gemini_ng"
    else:
        cache_dir = Path(cache_dir)

    cache_dir.mkdir(parents=True, exist_ok=True)

    return cache_dir


def get_cache_instance() -> Cache:
    global _CACHE

    if _CACHE is None:
        _CACHE = Cache(get_cache_dir())

    return _CACHE
