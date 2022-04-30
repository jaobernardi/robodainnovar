from pyding import on
import logging
from lib.structures import InternalActions
from lib import database


@on("whatsapp_new_message")
def new_message(event, whatsapp, message):
    logging.info(f"[{message.user.phonenumber}] {message.text}")
    match message.text.split(" "):
        case ["!ping"]:
            message.reply("Pong!")
        case ["!about"]:
            message.reply("*Whatpy* version *6.0.1-BETA* by _@jaobernard_")
        case ["!test", "video"]:
            message.reply("", file="assets/teste.mp4")
        case _:
            message.seen()
    
