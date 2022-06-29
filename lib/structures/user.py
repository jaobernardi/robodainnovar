from .. import database, utils
from . import Menu
from base64 import b64encode
import mimetypes
import os


class User():
    def __init__(self, phonenumber, id, name=None, whatsapp=None):
        self.phonenumber = phonenumber
        self.id = id
        self.name = name if name else ''
        self.fetch_database()
        self.whatsapp = whatsapp

    def __eq__(self, __o) -> bool:
        return self.phonenumber == __o.phonenumber

    @classmethod
    def no_id(cls, number, name, **extras):
        return cls(number, f'{number}@c.us', name, **extras) 

    @classmethod
    def from_phonenumber(cls, number):
        return cls(number, f'{number}@c.us')

    @property
    def vcard(self):
        return f'BEGIN:VCARD\nVERSION:3.0\nN:;{self.name or self.parsed_number};;;\nFN:{self.name or self.parsed_number}\nTEL;type=CELL;waid={self.phonenumber}:{self.parsed_number}\nEND:VCARD'

    @property
    def parsed_number(self):
        return utils.parse_number(self.phonenumber)

    @property
    def menu(self):
        return self._menu
    
    @menu.setter
    def menu(self, new_value: Menu):
        self._menu = new_value
        if self._menu:
            self._menu.context['user'] = self
        self.update_database()

    def fetch_database(self):
        response = database.get_user(self.phonenumber)
        if not response:
            database.create_user(self.phonenumber, self.name, [])
            self.permissions, self._menu = [], None
            return

        phonenumber, name, self.permissions, self._menu = response
        if name != self.name and self.name:
            self.update_database()
        else:
            self.name = name 
        
        if self._menu:
            self._menu.context['user'] = self

    def send_message(self, msg, file=None, contact=None):
        if not self.whatsapp:
            # TODO: Custom exception
            raise Exception("Missing whatsapp interface object")

        options = {}

        if contact:
            options['contactCard'] = contact.id
            options['contactCardName'] = contact.name or contact.phonenumber
            options['vcard'] = contact.vcard

        elif file:
            file = os.path.abspath(file)
            with open(file, "rb") as f:
                data = b64encode(f.read())
            options['attachment'] = {
                "data": data.decode("utf-8"),
                "mimetype": mimetypes.guess_type(os.path.abspath(file))[0],
                "filename": os.path.basename(file)
            }
        self.whatsapp.send_message(self.id, msg, options)


    def has_permission(self, permission):
        possible = list(self.permissions)
        match_tokens = permission.split(".")

        while len(possible) > 0:
            for perm in possible:
                test_tokens = perm.split(".")
                index = 0
                for token in test_tokens:
                    if match_tokens[index] == "*":
                        return True
                    if token == "*":
                        return True
                    if token != match_tokens[index]:
                        possible.remove(perm)
                        break
                    if index+1 == len(test_tokens) and index+1 == len(match_tokens):
                        return True
                    if index+1 >= len(match_tokens):
                        possible.remove(perm)
                        break
                    index += 1
        return False

    def update_database(self):
        database.update_user(self.phonenumber, self.name, self.permissions, self._menu)
    