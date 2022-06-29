import logging
from time import sleep
from pyding import on

from lib.structures import CardAction, User

logger = logging.getLogger(__name__)

@on("card_call", action=CardAction.BROADCAST)
def broadcast_cards(event, action, data, card, **extras):
    whatsapp = extras['whatsapp']
    recipients: list[User] = [User.no_id(**d, whatsapp=whatsapp) for d in data['recipients']]
    logger.info(f"Recieved broadcast invoke for '{card.name}' with {len(recipients)} recipients ")

    count = 0
    for recipient in recipients:
        logger.info(f"Broadcasting to {recipient.phonenumber}")
        if count >= 10:
            count = 0
            sleep(1)
        for msg in data['messages']:
            recipient.send_message(**msg)
            count += 1