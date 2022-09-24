import logging
from pyding import on
from lib.structures import User
from lib import config
from datetime import datetime
from . import messages


logger = logging.getLogger(__name__)


@on("menu_invite_status")
def atending_call(event, carryoption, user: User):
    whatsapp = user.whatsapp
    event_managers = [User.from_phonenumber('555492022338', whatsapp=whatsapp), User.from_phonenumber('555499763132', whatsapp=whatsapp)]
    event_id, status = carryoption.split("::")
    status = True if status == 'True' else False
    with open('confirmation_list.txt', 'a', encoding='utf-8') as file:
        file.write(f'"{user.phonenumber}";"{user.name}";"{event_id}";"{status}"\n')

    for manager in event_managers:
        if status == True:
            manager.send_message(f'Confirmação de Presença.\nO convidado {user.name} confirmou a sua presença e irá participar do evento _{event_id}_.')
        else:
            manager.send_message(f'Confirmação de Presença. 🎟\nO convidado {user.name} informou que*NÃO* irá participar do evento _{event_id}_.')
        manager.send_message("", contact=user)
