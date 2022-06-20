import importlib
import io
import sys
from pyding import on, EventCall, event_space
import logging
from . import atending_call
from lib.structures import InternalActions, Message, Menu
from lib.whatsapp import Whatsapp
from lib.structures.user import User
from contextlib import redirect_stdout


TEMPORARY_BLOCKS = []

logger = logging.getLogger(__name__)

@on("whatsapp_new_message")
def new_message(event: EventCall, whatsapp: Whatsapp, message: Message):
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
            message.reply("Pong!!!!")
        
        case ['!execute', 'script', script] if message.user.has_permission("commands.scripts.excecute"):
            whatsapp.load_js_from_file(f"bin/js/{script}")

        case ["!get", "user", user] if message.user.has_permission("commands.get.user"):
            message.reply("", contact=User(user, f"{user}@c.us"))

        case ["!debug", 'eval', *eval_text] if message.user.has_permission("commands.eval"):
            message.react('👩‍💻')
            eval_text = " ".join(eval_text)
            try:
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    code = compile(eval_text, '<exec>', 'single' if '\n' not in eval_text else 'exec')
                    exec(code, globals(), locals())
            except Exception as e:
                message.react('❌')
                message.reply(repr(e))
            else:
                message.react('✅')
                message.reply(f"```Código Executado:```\n{stdout.getvalue() or '_...</silêncio>..._'}")

        case ["!debug", "raise"] if message.user.has_permission("commands.eval"):
            raise Exception()

        case ['!get', 'global', variable] if message.user.has_permission("commands.get.globals"):
            message.reply(repr(globals()[variable]))

        case ['!get', 'locals', variable] if message.user.has_permission("commands.get.locals"):
            message.reply(repr(locals()[variable]))

        case ["!about"]:
            message.reply("*Whatpy* version *6.0.1-STABLE* by _@jaobernard_")

        case ["!reset"]:
            message.user.menu = None
            

        case ["!reload"] if message.user.has_permission("commands.reload"):
            event_space.global_event_space.unregister_from_module(atending_call)
            importlib.reload(atending_call)
            event_space.global_event_space.unregister_from_module(sys.modules[__name__])
            importlib.reload(sys.modules[__name__])
            message.reply("✅ Código recarregado", reaction='✅')

        
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
    
