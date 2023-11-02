from nereid.core.config import settings
from nereid.core.log import logging
from nereid.factory import create_app

logging.basicConfig(
    format="%(levelname)-9s %(name)s: %(message)s",
    level=settings.LOG_LEVEL,
)

app = create_app()
