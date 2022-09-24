from enum import Enum, auto
from json import load
import os
import pyding

from lib.structures.user import User, Menu


class CardAction(Enum):
    BROADCAST = auto()

class CardEffectType(Enum):
    SETMENU = auto()

class CardEffect():
    def __init__(self, type, extra):
        self.type = type
        self.extra = extra
    
    def apply(self, user: User):
        match self.type:
            case CardEffectType.SETMENU:
                user.menu = Menu(self.extra['name'], self.extra['carryOption'])
                if user.whatsapp:
                    user.send_message(user.menu.menu_string())
        

class CardEffects():
    def __init__(self, effects : list[CardEffect]):
        self.effects = effects

    def apply(self, *args, **kwargs):
        for effect in self.effects:
            effect.apply(*args, **kwargs)

    @classmethod
    def from_json(cls, data):
        effects:list[CardEffect] = []
        for effect in data:
            effects.append(CardEffect(
                                CardEffectType(effect["type"]),
                                effect["data"]
                            )
                        )
        return cls(effects)


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
        self.effects: CardEffects = CardEffects.from_json(data['effects']) if 'effects' in data else CardEffects([])

    def call(self, **extras):
        event = pyding.call("card_call", action=self.action, data=self.data, card=self, cancellable=True,**extras)
        rtr_message = (self.invoke_actions['call'] if 'call' in self.invoke_actions else '').format(card=self)
        return rtr_message, event