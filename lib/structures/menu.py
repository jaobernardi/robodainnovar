from enum import Enum, auto
from json import dumps, load, loads
from .. import config
from pathlib import Path

import pyding


class InternalActions(Enum):
    CARRYCHANGE = auto()
    MENUCHANGE = auto()
    REQUESTEDEND = auto()


class Menu():
    def __init__(self, name, carryoption=None, **context):
        self.name = name
        self.context = context
        self.carryoption = carryoption
        self.load()
    
    @property
    def options(self):
        if self.carryoption in self.data['options']:
            return self.data['options'][self.carryoption]
        return self.data['options']['*']

    @classmethod
    def fromDict(self, dict):
        return self(**dict)
    
    @classmethod
    def fromString(self, str):
        dict = loads(str)
        return self(**dict)

    @property
    def messages(self):
        return {k: v.format(**self.context) for k, v in self.data['messages'].items()}


    @property
    def fallbacks(self):
        return self.data['fallbacks']

    def __str__(self):
        return dumps({"name": self.name, "carryoption": self.carryoption})
    
    @staticmethod
    def dump(self):
        return self.__str__()


    def load(self):
        path = Path(config.get_menu_path()) / (self.name + ".json")
        file = open(path)
        self.data = load(file)
        file.close()
    
    def parse_action(self, action, context, event_context):
        for action in action.split("|$|"):
            action_context = action.split("#")[1].split("@")[0]
            arguments = "@".join(action.split("@")[1:])
            action = action.split("#")[0]

            arguments = arguments.format(**(self.__dict__ | context))

            match [action, action_context, arguments]:
                case ["exit", *any]:
                    return InternalActions.REQUESTEDEND

                case ["menu", menu_name, carryoption]:
                    self.__init__(menu_name, carryoption)
                    return InternalActions.MENUCHANGE
                
                case ["change", "carryoption", new_carry]:
                    self.carryoption = new_carry
                    return InternalActions.CARRYCHANGE

                case ["event", event_name, carryoption]:
                    event = pyding.call(event_name, carryoption=carryoption, **event_context)
    
    def has_option(self, option):
        return option in self.options

    def option_action(self, option):
        if 'action' in self.options[option]:
            return self.options[option]['action']
        return self.fallbacks['action']

    def get_option(self, option):
        if option in self.options:
            return option
        elif "*" in self.options:
            return '*'

    def process_option(self, option, **context):
        if not self.has_option(option):
            # TODO: Custom exceptions
            raise Exception()
        
        option = self.get_option(option)

        action = self.option_action(option)
        return self.parse_action(action, context=self.options[option] | {"input": option} | self.context, event_context=context | self.context)

    def menu_string(self):
        lines = [self.data['prompt']]
        for (index, option) in self.options.items():
            if index == "*":
                continue
            if option['index_name']:
                index = option['index_name']
            if "name" in option:
                index = option['screen_name']
            lines.append(f"{index} — {option['prompt']}")
        return "\n".join(lines)