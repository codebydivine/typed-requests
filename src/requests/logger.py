import sys
import traceback

ENABLE_DEBUG = False

class MockLogger:
    def __init__(self, name: str):
        self.name = name

    def _log(self, level: str, msg: str, exc_info: bool):
        if exc_info:
            sys.stdout.write(f"{level}:{self.name}:{msg}\n{traceback.format_exc()}\n")
        else:
            sys.stdout.write(f"{level}:{self.name}:{msg}\n")

    def info(self, msg, exc_info=False):
        self._log("INFO", msg, exc_info)

    def debug(self, msg, exc_info=False):
        if ENABLE_DEBUG:
            self._log("DEBUG", msg, exc_info)

    def error(self, msg, exc_info=False):
        self._log("ERROR", msg, exc_info)

    def warning(self, msg, exc_info=False):
        self._log("WARNING", msg, exc_info)

# Function to get logger for a specific module
def get_logger(name):
    return MockLogger(name)
