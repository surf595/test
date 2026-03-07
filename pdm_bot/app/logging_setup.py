import logging


def setup_logging() -> logging.Logger:
    logging.basicConfig(
        format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
        level=logging.INFO,
    )
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("telegram.ext").setLevel(logging.INFO)
    return logging.getLogger("pdm_bot")
