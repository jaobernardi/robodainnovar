import logging
import os
import sys
import traceback

logger = logging.getLogger(__name__)

import inspect


class InitializeArguments:
    """
    Automaticly casts the items in a function's args annotation
    """
    def __init__(self, function):
        self.function = function

    @property
    def arguments(self):
        sig_values = list(inspect.signature(self.function).parameters.values())
        return sig_values

    def __call__(self, *args, **kwargs):
        # Default arguments to None
        input_args = {k.name: None for k in self.arguments}

        # Build input keyword arguments
        for arg_value, arg in zip(args, self.arguments):
            input_args[arg.name] = arg.annotation(arg_value) if arg.annotation not in [arg.empty, None] else arg_value
        
        for arg_name, arg_value, arg in zip(kwargs.keys(), kwargs.values(), self.arguments):
            input_args[arg_name] = arg.annotation(arg_value) if arg.annotation not in [arg.empty, None] else arg_value

        # Call the function
        return self.function(**input_args)

def load_handlers():
    for handler in os.listdir("handlers"):
        if handler.endswith(".py"):
            try:
                __import__("handlers."+handler.removesuffix(".py"))
            except:
                logger.error(f"Failed to load handler {handler}")
                traceback.print_exc(file=sys.stdout)
