"""
Configure and expose the application logger.

- Use get_logger() to access the global logger.
- Implement log level and format configuration here.
- Can be based on logging or structlog.

Recommended: inject logger into services or repositories for better traceability.
"""

import logging
from logging import Logger

from src.core.config import cfg

logger: Logger = logging.getLogger("app")


def configure_logger() -> None:
    log_level = cfg.logging.level.upper()
    allowed_levels = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }
    level = allowed_levels.get(log_level, logging.INFO)

    logging.basicConfig(
        level=level, format="%(asctime)s | %(levelname)s | %(filename)s:%(lineno)d | %(message)s"
    )

    logger.setLevel(level)


def get_logger() -> Logger:
    return logger


def main() -> None:
    configure_logger()
    get_logger().debug("Test message from main()")


if __name__ == "__main__":
    main()
