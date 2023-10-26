from nereid.core.config import settings
from nereid.core.log import logging
from nereid.factory import create_app

logging.basicConfig(level=settings.LOG_LEVEL)

app = create_app()
