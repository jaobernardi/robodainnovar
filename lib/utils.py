import logging
import os
import sys
import traceback


def load_handlers():
    for handler in os.listdir("handlers"):
        if handler.endswith(".py"):
            try:
                __import__("handlers."+handler.removesuffix(".py"))
            except:
                logging.error(f"Failed to load handler {handler}")
                traceback.print_exc(file=sys.stdout)