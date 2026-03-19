import logging
from logging.handlers import TimedRotatingFileHandler
import os


def configure_logging(
    log_folder: str = "logs",
    app_name: str = "app",
    backup_count: int = 5,
    console_level: int = logging.INFO,
    file_level: int = logging.DEBUG,
) -> None:
    root = logging.getLogger()

    if getattr(root, "_configured", False):
        return

    root.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    os.makedirs(log_folder, exist_ok=True)

    combined = TimedRotatingFileHandler(
        os.path.join(log_folder, f"{app_name}_combined_utc.log"),
        when="midnight",
        interval=1,
        backupCount=backup_count,
        encoding="utf-8",
        utc=True,
    )
    combined.suffix = "%Y-%m-%d"
    combined.setLevel(file_level)
    combined.setFormatter(formatter)

    error = TimedRotatingFileHandler(
        os.path.join(log_folder, f"{app_name}_error_utc.log"),
        when="midnight",
        interval=1,
        backupCount=backup_count,
        encoding="utf-8",
        utc=True,
    )
    error.suffix = "%Y-%m-%d"
    error.setLevel(logging.ERROR)
    error.setFormatter(formatter)

    console = logging.StreamHandler()
    console.setLevel(console_level)
    console.setFormatter(formatter)

    root.addHandler(combined)
    root.addHandler(error)
    root.addHandler(console)

    root._configured = True


def get_custom_logger(app_name: str = "app") -> logging.Logger:
    return logging.getLogger(app_name)


logging.getLogger("urllib3").setLevel(logging.WARNING)
