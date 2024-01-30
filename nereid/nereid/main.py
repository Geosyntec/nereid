import logging
import logging.config

from nereid.core.config import LOGGING_CONFIG
from nereid.factory import create_app

app = create_app()


def main():
    import argparse

    import uvicorn
    import uvicorn.config

    from nereid.core.utils import merge_dicts

    logging.config.dictConfig(config=LOGGING_CONFIG)
    logger = logging.getLogger("nereid")

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--host", help="Bind socket to this host.  [default: 127.0.0.1]", type=str
    )
    parser.add_argument(
        "--port",
        help="Bind socket to this port. If 0, an available port will be picked.  [default: 8000].",
        type=int,
    )
    parser.add_argument(
        "--reload", help="Enable auto-reload.", action="store_true", default=False
    )

    args, unk = parser.parse_known_args()
    kwargs = {k: v for k, v in vars(args).items() if v is not None}

    # logger.warning("warning message with extras", extra={"x": "hello"})

    if unk:
        logger.warning(f'ignored arguments: {" ".join(unk)}')

    config = merge_dicts(uvicorn.config.LOGGING_CONFIG, LOGGING_CONFIG)

    uvicorn.run("nereid.factory:create_app", factory=True, **kwargs, log_config=config)


if __name__ == "__main__":
    main()
