from pyding import on, call
import logging
from lib.structures import InternalActions, Message, Menu
from lib import database
from lib.structures.user import User

TEMPORARY_BLOCKS = []

logger = logging.getLogger(__name__)

@on("whatsapp_new_message")
def new_message(event, whatsapp, message: Message):

    logger.debug('-- MESSAGE CHECKS --')
    logger.debug(f'CHECK: {int(message.user.phonenumber)} in {TEMPORARY_BLOCKS}? {message.user.phonenumber in TEMPORARY_BLOCKS}')
    logger.debug(f'CHECK: {message.type} == "e2e_notification"? {message.type == "e2e_notification"}')
    logger.debug(f'CHECK: not {message.text}? {not message.text}')
    logger.debug(f'SUB CHECK: {message.type} == "e2e_notification" or not {message.text}? {message.type == "e2e_notification" or not message.text}')
    logger.debug(f'FINAL CHECK: {message.user.phonenumber} in {TEMPORARY_BLOCKS} and ({message.type} == "e2e_notification" or not {message.text})? {message.user.phonenumber in TEMPORARY_BLOCKS and (message.type == "e2e_notification" or not message.text)}')
    logger.debug('-- END MESSAGE CHECKS --')

    if int(message.user.phonenumber) in TEMPORARY_BLOCKS and (message.type == 'e2e_notification' or not message.text):
        TEMPORARY_BLOCKS.remove(message.user.phonenumber)
        return
    
    logger.info(f"[{message.user.phonenumber}] {message.text}")
    text = message.text.split(" ") if message.text else None
    match text:

        case ["!reaction", reaction]:
            message.reply("Okie dokie", reaction=reaction)
        case ["!ping"]:
            message.reply("Pong!")
        
        case ["!about"]:
            message.reply("*Whatpy* version *6.0.1-BETA* by _@jaobernard_")

        case ["!set", "menu", menu]:
            message.user.menu = Menu(menu)
            message.user.update_database()
            message.reply(message.user.menu.messages['welcome'], reaction="👋")
            message.reply(message.user.menu.menu_string())

        case msg:
            if not message.user.menu or not msg:
                message.user.menu = Menu("citySelect")
                message.user.update_database()
                if "welcome" in message.user.menu.messages:
                    message.reply(message.user.menu.messages['welcome'], reaction="👋")
                message.reply(message.user.menu.menu_string(), qoute=False)
                return
            if not msg:
                return
            
            msg = " ".join(msg)
            if not message.user.menu.has_option(msg):
                if "wrong" not in message.user.menu.messages:
                    message.reply("Opção Inválida", reaction="🙅‍♀️")
                else:
                    message.reply(message.user.menu.messages['wrong'], reaction="🙅‍♀️")
                return

            response = message.user.menu.process_option(msg)
            if response == InternalActions.MENUCHANGE:
                message.reply(message.user.menu.menu_string(), reaction='✅')
            elif response == InternalActions.REQUESTEDEND:
                if "end" not in message.user.menu.messages:
                    message.reply("</Menu encerrou-se e não deixou nenhuma mensagem de saída.>")
                else:
                    message.reply(message.user.menu.messages['end'])
                
                message.user.menu = None
            
            message.user.update_database()
    
