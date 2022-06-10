from pyding import on
from lib.structures import User
from lib import config
from datetime import datetime



@on("menu_atending_call")
def atending_call(event, carryoption, user: User):
    selector = carryoption.split("::")
    whatsapp = user.whatsapp
    atendees = {k: {'user': User(v, f"{v['number']}@c.us", k, whatsapp), 'cities': v['cities']} for k, v in config.get_contact()['financeiro'].items()}
    
    
    match selector:
        case [city, "Financeiro", operation]:
            if city == 'outside': city = 'Outra cidade'
            print(city, atendees)
            for operator_name, operator_info in atendees.items():

                print(city, operator_info['cities'])
                if city in operator_info['cities']:
                    operator = operator_info['user']
                    print(operator.id)
                    now = datetime.now()
                    operator.send_message((
                        f"📥 — Requisição de atendimento. (Financeiro)\n"
                        f"Olá {operator_name}! 👋\n"
                        f"Hoje às {now.hour}h{f'{now.minute}min' if now.minute > 0 else ' '}, "
                        f"{user.name} solicitou um atendimento {f'referente à _{operation}_ ' if operation != 'other' else ''}"
                        f"na região de {city}. *Aqui está o contato:*"    
                    ))
                    operator.send_message("", contact=user)
        case [city, "Comercial", operation]:
            if city == 'outside': city = 'Outra cidade'
            
            operator = User(config.get_contact()['comercial']['number'], f"{config.get_contact()['comercial']['number']}@c.us", whatsapp=whatsapp)
            #operator = user
            now = datetime.now()
            operator.send_message((
                f"📥 — Requisição de atendimento. (Comercial)\n"
                f"Olá 👋\n"
                f"Hoje às {now.hour}h{f'{now.minute}min' if now.minute > 0 else ' '}, "
                f"{user.name} solicitou um atendimento {f'referente à _{operation}_ ' if operation != 'other' else ''}"
                f"na região de {city}. *Aqui está o contato:*"    
            ))
            operator.send_message("", contact=user)
        
        case [city, "Engenharia", operation]:
            if city == 'outside': city = 'Outra cidade'

            operator = User(config.get_contact()['engenharia'][operation]['number'], f"{config.get_contact()['engenharia'][operation]['number']}@c.us", whatsapp=whatsapp)
            #operator = user
            now = datetime.now()
            operator.send_message((
                f"📥 — Requisição de atendimento. (Engenharia)\n"
                f"Olá 👋\n"
                f"Hoje às {now.hour}h{f'{now.minute}min' if now.minute > 0 else ' '}, "
                f"{user.name} solicitou um atendimento {f'referente à _{operation}_ ' if operation != 'other' else ''}"
                f"na região de {city}. *Aqui está o contato:*"    
            ))
            operator.send_message("", contact=user)
        
        case [city, "Atendimento Geral", operation]:
            if city == 'outside': city = 'Outra cidade'

            operator = User(config.get_contact()['atendimento geral']['number'], f"{config.get_contact()['atendimento geral']['number']}@c.us", whatsapp=whatsapp)
            #operator = user
            now = datetime.now()
            operator.send_message((
                f"📥 — Requisição de atendimento. (Atendimento Geral)\n"
                f"Olá 👋\n"
                f"Hoje às {now.hour}h{f'{now.minute}min' if now.minute > 0 else ' '}, "
                f"{user.name} solicitou um atendimento {f'referente à _{operation}_ ' if operation != 'other' else ''}"
                f"na região de {city}. *Aqui está o contato:*"    
            ))
            operator.send_message("", contact=user)
        
        