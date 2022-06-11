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
    logger.debug(f'CHECK: {repr(message.user.phonenumber)} in {repr(TEMPORARY_BLOCKS)}? {message.user.phonenumber in TEMPORARY_BLOCKS}')
    logger.debug(f'CHECK: {repr(message.type)} == "e2e_notification"? {message.type == "e2e_notification"}')
    logger.debug(f'CHECK: not {repr(message.text)}? {not message.text}')
    logger.debug(f'SUB CHECK: {repr(message.type)} == "e2e_notification" or not {repr(message.text)}? {message.type == "e2e_notification" or not message.text}')
    logger.debug(f'FINAL CHECK: {repr(message.user.phonenumber)} in {repr(TEMPORARY_BLOCKS)} and ({repr(message.type)} == "e2e_notification" or not {repr(message.text)})? {message.user.phonenumber in TEMPORARY_BLOCKS and (message.type == "e2e_notification" or not message.text)}')
    logger.debug('-- END MESSAGE CHECKS --')

    if int(message.user.phonenumber) in TEMPORARY_BLOCKS and (message.type == 'e2e_notification' or not message.text):
        TEMPORARY_BLOCKS.remove(message.user.phonenumber)
        return
    
    logger.info(f"[{message.user.phonenumber}] {message.text}")
    text = message.text.split(" ") if message.text else None
    match text:

        case ["!send", "assets"] if message.user.has_permission("commands.send.assets"):
            message.reply("Caption", file='assets/teste.jpeg')

        case ["!send", "reaction", reaction] if message.user.has_permission("commands.send.reactions"):
            message.reply('', reaction=reaction)

        case ["!ping"] if message.user.has_permission("commands.ping"):
            message.reply("Pong!")
        
        case ['!execute', 'script', script] if message.user.has_permission("commands.scripts.excecute"):
            whatsapp.load_js_from_file(f"bin/js/{script}")

        case ["!get", "user", user] if message.user.has_permission("commands.get.user"):
            message.reply("", contact=User(user, f"{user}@c.us"))

        case ['!get', 'global', variable] if message.user.has_permission("commands.get.globals"):
            message.reply(repr(globals()[variable]))

        case ['!get', 'locals', variable] if message.user.has_permission("commands.get.locals"):
            message.reply(repr(locals()[variable]))

        case ["!about"]:
            message.reply("*Whatpy* version *6.0.1-BETA* by _@jaobernard_")

        case ["!set", "menu", menu] if message.user.has_permission("commands.set.menu"):
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
    
