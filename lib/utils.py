import logging
import os
import sys
import traceback

from tendo import singleton

logger = logging.getLogger(__name__)

import inspect

def aquire_lock() -> singleton.SingleInstance:
    return singleton.SingleInstance()

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

def load_handlers(basename):
    for handler in os.listdir("handlers"):
        if handler.endswith(".py"):
            try:
                __import__("handlers."+handler.removesuffix(".py"))
                logging.getLogger('handlers.'+handler.removesuffix(".py")).addHandler(
                    logging.FileHandler(
                        'logs/'+basename+'-handlers.'+handler.removesuffix(".py")+".log"
                    )
                )
                logger.info(f'Loaded {handler}')
            except:
                logger.error(f"Failed to load handler {handler}")
                traceback.print_exc(file=sys.stdout)

@InitializeArguments
def parse_number(number: str):
    country_code, ddd, first, second = "", "", "", ""
    index = 0
    for int in number:
        if index in [0, 1]:
            country_code += int
        elif index in [2, 3]:
            ddd += int
        elif index in [4,5,6,7]:
            first += int
        else:
            second += int
        index += 1
    return f"+{country_code} {ddd} {first}-{second}"