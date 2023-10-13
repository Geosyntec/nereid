import logging

from nereid.core.config import settings
from nereid.factory import create_app

logging.basicConfig(level=settings.LOG_LEVEL)

app = create_app()
