import importlib
import io
import sys
from pyding import on, EventCall, event_space, call
import logging

from . import atending_call, broadcast_cards
from lib.structures import InternalActions, Message, Menu, Card
from lib.whatsapp import Whatsapp
from lib.structures.user import User
from contextlib import redirect_stdout


TEMPORARY_BLOCKS = []

logger = logging.getLogger(__name__)

@on("whatsapp_new_message")
def new_message(event: EventCall, whatsapp: Whatsapp, message: Message):
    if int(message.user.phonenumber) in TEMPORARY_BLOCKS and (message.type == 'e2e_notification' or not message.text):
        TEMPORARY_BLOCKS.remove(message.user.phonenumber)
        return
    
    logger.info(f"[{message.user.phonenumber}] {message.text}")
    text = [i.lower() for i in message.text.split(" ")] if message.text else None
    match text:

        case ["!send", "assets"] if message.user.has_permission("commands.send.assets"):
            message.reply("Caption", file='assets/teste.jpeg')

        case ["!send", "reaction", reaction] if message.user.has_permission("commands.send.reactions"):
            message.reply('', reaction=reaction)

        case ["!ping"] if message.user.has_permission("commands.ping"):
            message.reply("Pong!!!!")
        
        case ['!execute', 'script', script] if message.user.has_permission("commands.scripts.excecute"):
            whatsapp.load_js_from_file(f"bin/js/{script}")

        case ["!get", "user", user] if message.user.has_permission("users.get"):
            message.reply("", contact=User(user, f"{user}@c.us"))

        case ["!get", "user", user, "permissions"] if message.user.has_permission("users.get.permissions"):
            user = User(user, f"{user}@c.us")
            message.reply(f"This user has the following permissions: {', '.join(user.permissions)}")

        case ["!add", "permission", permission, "to", user] if message.user.has_permission("users.add.permission") and message.user.has_permission(permission):
            user = User.from_phonenumber(user)
            user.permissions.append(permission)
            user.update_database()
            message.react('✅')
            message.reply(f"Added permission {permission} to {user.name or user.phonenumber}")

        case ["!remove", "permission", permission, "from", user] if message.user.has_permission("users.remove.permission") and message.user.has_permission(permission):
            user = User.from_phonenumber(user)
            if permission in user.permissions:
                user.permissions.remove(permission)
            user.update_database()
            message.react('✅')
            message.reply(f"Removed permission {permission} from {user.name or user.phonenumber}")


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

        case ["!debug", "force", user, message_id]:
            call("whatsapp_new_message", whatsapp=whatsapp, message=Message())

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
        
        case ["👍"] | ["muito", "obrigado" | "obrigada"] | ["valeu"] | ["obrigado" | "obrigada"]:
            message.reply("Disponha! Se tiver qualquer outra solicitação, basta enviar outra mensagem que lhe enviarei o menu de opções 😉")

        case ["!reload"] if message.user.has_permission("commands.reload"):
            event_space.global_event_space.unregister_from_module(atending_call)
            importlib.reload(atending_call)
            event_space.global_event_space.unregister_from_module(broadcast_cards)
            importlib.reload(broadcast_cards)
            event_space.global_event_space.unregister_from_module(sys.modules[__name__])
            importlib.reload(sys.modules[__name__])
            message.reply("✅ Código recarregado", reaction='✅')

        case ["!load", "card", card, "override", *parameters] if message.user.has_permission("commands.cards.invoke"):
            card = Card(card)
            extras = {}
            for parameter in parameters:
                parameter: str
                if parameter == "recipients":
                    extras["recipient_override"] = message.user
                if parameter.startswith("recipient_as="):
                    extras["recipient_override"] = User.from_phonenumber(parameter.removeprefix("recipient_as="), whatsapp=whatsapp)
            
            invoke_msg, event = card.call(whatsapp=whatsapp, **extras)
            message.reply(invoke_msg if not event.cancelled else '❌ — A execução deste card foi cancelado pelo filtro.')

        case ["!load", "card", card] if message.user.has_permission("commands.cards.invoke"):
            card = Card(card)
            invoke_msg, event = card.call(whatsapp=whatsapp)
            message.reply(invoke_msg if not event.cancelled else '❌ — A execução deste card foi cancelado pelo filtro.')

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
    
