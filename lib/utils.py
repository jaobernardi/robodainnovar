import logging
import os
import sys
import traceback
from itertools import zip_longest
from typing import Any, ValuesView

from tendo import singleton

logger = logging.getLogger(__name__)
logger.addHandler(
                    logging.FileHandler(
                        'logs/'+'utils.log', encoding="utf-8"
                    )
                )
import inspect

def aquire_lock() -> singleton.SingleInstance:
    return singleton.SingleInstance()

class AnnotationDefaults:
    """
    Automaticly casts the items in a function's args annotation
    """
    def __init__(self, function):
        self.function = function

    @property
    def arguments(self):
        sig_values : list[inspect.ValuesView[inspect.Parameter]] = list(inspect.signature(self.function).parameters.values())
        return sig_values

    @staticmethod
    def define_value(arg, value):
        output: Any = value
        if arg.annotation not in [arg.empty, None]:
            # If there is a annotation on the function                
            if not value:
                # create an instance of the annotation
                output = arg.annotation()
            elif not isinstance(value, arg.annotation):
                # cast into the annotation
                output = arg.annotation(value)
        return output

    def __call__(self, *args, **kwargs):
        # Default arguments to None
        input_args = {k.name: None for k in self.arguments}

        # Build input keyword arguments
        for arg_value, arg in zip(args, self.arguments):
            input_args[arg.name] = self.define_value(arg, arg_value)

        for arg_name, arg_value, arg in zip_longest(kwargs.keys(), kwargs.values(), self.arguments):
            if not arg_name: break
            input_args[arg_name] = self.define_value(arg, arg_value)

        # Call the function
        return self.function(**input_args)

def load_handlers():
    for handler in os.listdir("handlers"):
        if handler.endswith(".py"):
            try:
                __import__("handlers."+handler.removesuffix(".py"))
                logging.getLogger('handlers.'+handler.removesuffix(".py")).addHandler(
                    logging.FileHandler(
                        'logs/'+'handlers.'+handler.removesuffix(".py")+".log"
                    )
                )
                logger.info(f'Loaded {handler}')
            except:
                logger.error(f"Failed to load handler {handler}")
                traceback.print_exc(file=sys.stdout)

@AnnotationDefaults
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