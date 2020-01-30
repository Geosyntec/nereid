import functools
import hashlib
import logging

import redis

logger = logging.getLogger(__name__)


redis_cache = redis.Redis(host="redis", port=6379, db=9)

try:
    # It's ok if redis isn't up, we'll fall back to an lru_cache if we can only
    # use the main process. If redis is available, let's flush the cache to start
    # fresh.
    if redis_cache.ping():
        redis_cache.flushdb()
        logger.debug("flushed redis function cache")
except redis.ConnectionError:
    pass


def rcache(**rkwargs):
    ex = rkwargs.pop("ex", 3600 * 24)

    def _rcache(obj):
        cache = redis_cache

        @functools.wraps(obj)
        def memoizer(*args, **kwargs):
            sorted_kwargs = {k: kwargs[k] for k in sorted(kwargs.keys())}

            # hashing the key may not be necessary, but it keeps the server-side filepaths hidden
            key = hashlib.sha1(
                (str(args) + str(sorted_kwargs)).encode("utf-8")
            ).hexdigest()

            if cache.get(key) is None:
                logger.debug(f"redis cache miss {key}")

                cache.set(key, obj(*args, **kwargs), ex=ex)

            else:
                logger.debug(f"redis hit cache {key}")

            return cache.get(key)

        return memoizer

    return _rcache


def lru_cache(**rkwargs):
    maxsize = rkwargs.pop("maxsize", 128)
    typed = rkwargs.pop("typed", False)
    logger.debug("cached with functools.lru_cache")

    return functools.lru_cache(maxsize=maxsize, typed=typed)


def get_cache_decorator():
    """fetch a cache decorator for functions. If redis is up,
    use that, else use lru_cache.

    The point of the lru fallback is to make development easier.
    In production and even in CI this should use the redis cache.
    Sometimes it's nice for things that can be separate to be
    separate; like during development, local testing, and benchmarking.

    """
    try:
        if redis_cache.ping():
            return rcache
        else:
            return lru_cache
    except redis.ConnectionError:
        return lru_cache


cache_decorator = get_cache_decorator()
