from pyding import on
import logging
from lib.structures import InternalActions, Message, Menu
from lib import database


@on("whatsapp_new_message")
def new_message(event, whatsapp, message: Message):
    logging.info(f"[{message.user.phonenumber}] {message.text}")
    text = message.text.split(" ") if message.text else None
    match text:
        case ["!ping"]:
            message.reply("Pong!")
        
        case ["!about"]:
            message.reply("*Whatpy* version *6.0.1-BETA* by _@jaobernard_")

        case ["!set", "menu", menu]:
            message.user.menu = Menu(menu)
            message.user.update_database()
            message.reply(message.user.menu.menu_string())

        case msg:
            if not message.user.menu or not msg:
                message.user.menu = Menu("citySelect")
                message.user.update_database()
                if "welcome" in message.user.menu.messages:
                    message.reply(message.user.menu.messages['welcome'])
                message.reply(message.user.menu.menu_string(), qoute=False)
                return

            msg = " ".join(msg)
            if not message.user.menu.has_option(msg):
                if "wrong" not in message.user.menu.messages:
                    message.reply("Opção Inválida")
                else:
                    message.reply(message.user.menu.messages['wrong'])
                return

            response = message.user.menu.process_option(msg)
            if response == InternalActions.MENUCHANGE:
                message.reply(message.user.menu.menu_string())
            elif response == InternalActions.REQUESTEDEND:
                if "end" not in message.user.menu.messages:
                    message.reply("<Menu encerrou-se>")
                else:
                    message.reply(message.user.menu.messages['end'])
                
                message.user.menu = None
            
            message.user.update_database()
    
