import logging
from pyding import on
from lib.structures import User
from lib import config
from datetime import datetime
from . import messages


logger = logging.getLogger(__name__)


@on("menu_atending_call")
def atending_call(event, carryoption, user: User):
    selector = carryoption.split("::")
    whatsapp = user.whatsapp


    city, department, operation = selector
    
    logger.debug(f'Calling an operator for {city} with option {operation} in the department {department}')

    if department in config.get_atendings():
        department_options = config.get_atendings()[department]

        if city in department_options:
            logger.debug(f'Getting operators via the city')
            option_atendings = department_options[city]
        elif operation in department_options:
            logger.debug(f'Getting operators via the option')
            option_atendings = department_options[operation]
        elif '*' in department_options:
            logger.debug(f'Getting operators via the default')
            option_atendings = department_options['*']
        else:
            logger.debug(f'No operator found.')
            return
        
        for atending in option_atendings:
            logger.debug(f'Contacting operator {atending["name"]}')
            operator = User(atending['number'], f"{atending['number']}@c.us", atending['name'], whatsapp)
            now = datetime.now()
            operator.send_message((
                f"📥 — Requisição de atendimento. ({department})\n"
                f"Olá {atending['name']}! 👋\n"
                f"Hoje às {now.hour}h{f'{now.minute}min' if now.minute > 0 else ' '}, "
                f"{user.name} solicitou um atendimento {f'referente à _{operation}_ ' if operation != 'other' else ''}"
                f"na região de {city}. *Aqui está o contato:*"    
            ))
            operator.send_message("", contact=user)
            logger.debug(f'Finished contacting.')

    return