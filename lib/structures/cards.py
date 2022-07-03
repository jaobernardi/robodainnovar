from enum import Enum, auto
from json import load
import os
import pyding


class CardAction(Enum):
    BROADCAST = auto()


class Card():
    def __init__(self, filename):
        self.load(filename)
    
    def load(self, filename):
        with open(os.path.join("cards", filename+".json"), "rb") as file:
            data = load(file)
        self.name = data['name']
        self.action = CardAction(data['type'])
        self.data = data['data']
        self.disabled = data['disabled']
        self.invoke_actions = data['invoke']

    def call(self, **extras):
        event = pyding.call("card_call", action=self.action, data=self.data, card=self, cancellable=True,**extras)
        rtr_message = (self.invoke_actions['call'] if 'call' in self.invoke_actions else '').format(card=self)
        return rtr_message, event