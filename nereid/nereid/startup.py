import os

from tenacity import retry
from tenacity.after import after_log
from tenacity.before import before_log
from tenacity.stop import stop_after_attempt
from tenacity.wait import wait_fixed

from nereid.core.log import logging

logger = logging.getLogger(__name__)

CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")

wait_seconds = 1
try_for_minutes = 5
max_tries = int(60 / wait_seconds * try_for_minutes)


@retry(
    stop=stop_after_attempt(max_tries),
    wait=wait_fixed(wait_seconds),
    before=before_log(logger, logging.INFO),
    after=after_log(logger, logging.WARN),
)
def get_redis():
    import redis

    redis_conn = redis.Redis.from_url(CELERY_BROKER_URL)
    try:
        assert redis_conn.ping()
    except Exception as e:
        logger.error(e)
        raise e


@retry(
    stop=stop_after_attempt(max_tries),
    wait=wait_fixed(wait_seconds),
    before=before_log(logger, logging.INFO),
    after=after_log(logger, logging.WARN),
)
def get_worker():
    import nereid.bg_worker as bg

    try:
        bg.background_ping.apply_async().get(timeout=0.2)
    except Exception as e:
        logger.error(e)
        raise e


def start_nereid():
    logger.info("initializing nereid engine pre-start...")
    get_redis()
    get_worker()
    logger.info("nereid engine pre-start complete.")


def start_worker():
    logger.info("initializing nereid engine worker pre-start...")
    get_redis()
    logger.info("nereid engine worker pre-start complete.")


if __name__ == "__main__":
    import sys

    globals()[sys.argv[1]]()
