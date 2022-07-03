import logging
from time import sleep
from pyding import on

from lib.structures import CardAction, User
from lib.whatsapp import Whatsapp

logger = logging.getLogger(__name__)

@on("card_call", action=CardAction.BROADCAST)
def broadcast_cards(event, action, data, card, **extras):
    recipients: list[User]
    whatsapp: Whatsapp = extras['whatsapp']
    if 'recipient_override' in extras:
        recipients = [extras['recipient_override']]
    else:
        recipients = [User.no_id(**d, whatsapp=whatsapp) for d in data['recipients']]
    logger.info(f"Recieved broadcast invoke for '{card.name}' with {len(recipients)} recipients ")

    count = 0
    for recipient in recipients:
        logger.info(f"Broadcasting to {recipient.phonenumber}")
        if count >= len(data['messages'])*3:
            count = 0
            sleep(0.5)
        for msg in data['messages']:
            recipient.send_message(**msg)
            count += 1