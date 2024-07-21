from datetime import datetime
from enum import Enum

import sys

class Logger:
    @staticmethod
    def LOG(level, msg, *args):
        current_datetime = datetime.now()
        timenow = current_datetime.strftime("%H:%M:%S")

        levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if level < 0 or level >= len(levels):
            level = 0
        level_name = levels[level]
        # print(f"=> {msg.format(*args)}", file=sys.stderr)
        print(f"[{timenow}-{level_name}] {msg.format(*args)}", file=sys.stderr)