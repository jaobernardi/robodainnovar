import logging
from time import sleep
from pyding import on, EventCall

from lib.structures import CardAction, User, Card
from lib.whatsapp import Whatsapp

logger = logging.getLogger(__name__)

@on("card_call", priority=float('inf'))
def card_filter(event: EventCall, action, data, card: Card, **extras):
    if card.disabled:
        event.cancel()