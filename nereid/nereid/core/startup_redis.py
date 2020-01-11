from time import sleep
from pathlib import Path

import pandas
import redis
from redis import ConnectionError


redis_cache = redis.Redis(host="redis", db=9)


def load_reference_data():

    directory = Path("nereid/data")

    dct = {}
    files = directory.glob("**/*.csv")

    for f in files:
        key = str(f.parent / f.stem)
        dct[key] = pandas.read_csv(f).to_json(orient="table")

    redis_cache.mset(dct)


def init():  # pragma: no cover
    print("nereid-init-redis: initializing reference data cache...")

    for i in range(10):
        try:
            rsp = redis_cache.ping()
            if rsp:
                print("nereid-init-redis: redis is connected")
                break

        except ConnectionError:
            print(
                f"nereid-init-redis: waiting for redis server to pong. Attempt: {i+1}"
            )
            sleep(1)

    load_reference_data()
    print("nereid-init-redis: reference data initialized.")


if __name__ == "__main__":  # pragma: no cover
    init()
