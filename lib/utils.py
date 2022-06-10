import logging
import os
import sys
import traceback

logger = logging.getLogger(__name__)

def load_handlers():
    for handler in os.listdir("handlers"):
        if handler.endswith(".py"):
            try:
                __import__("handlers."+handler.removesuffix(".py"))
            except:
                logger.error(f"Failed to load handler {handler}")
                traceback.print_exc(file=sys.stdout)