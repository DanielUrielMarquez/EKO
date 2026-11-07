
import logging

from app.core.config import settings


def setup_logging() -> None:
    log_level = settings.LOG_LEVEL.upper()

    if log_level not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
        log_level = "INFO"

    logging.basicConfig(
        level=log_level,
        format=(
            "%(asctime)s | "
            "%(levelname)s | "
            "%(name)s | "
            "%(message)s"
        ),
        datefmt="%Y-%m-%d %H:%M:%S",
    )
