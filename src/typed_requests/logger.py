import sys
import traceback

ENABLE_DEBUG = False


class MockLogger:
    """Lightweight logger for divine-typed-requests."""

    __slots__ = ("name",)

    def __init__(self, name: str):
        self.name = name

    def _log(self, level: str, msg: str, exc_info: bool = False):
        """Write log message to stdout."""
        if exc_info:
            sys.stdout.write(f"{level}:{self.name}:{msg}\n{traceback.format_exc()}\n")
        else:
            sys.stdout.write(f"{level}:{self.name}:{msg}\n")

    def info(self, msg: str, exc_info: bool = False):
        """Log info message."""
        self._log("INFO", msg, exc_info)

    def debug(self, msg: str, exc_info: bool = False):
        """Log debug message if debug is enabled."""
        if ENABLE_DEBUG:
            self._log("DEBUG", msg, exc_info)

    def error(self, msg: str, exc_info: bool = False):
        """Log error message."""
        self._log("ERROR", msg, exc_info)

    def warning(self, msg: str, exc_info: bool = False):
        """Log warning message."""
        self._log("WARNING", msg, exc_info)


def get_logger(name: str) -> MockLogger:
    """Get a logger for a specific module."""
    return MockLogger(name)
