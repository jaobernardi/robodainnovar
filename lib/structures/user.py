from .. import database
from base64 import b64encode
import mimetypes
import os


class User():
    def __init__(self, phonenumber, id, name=None, whatsapp=None):
        self.phonenumber = phonenumber
        self.id = id
        self.name = name
        self.fetch_database()
        self.whatsapp = whatsapp
    

    def fetch_database(self):
        response = database.get_user(self.phonenumber)
        if not response:
            database.create_user(self.phonenumber)
            self.name, self.permissions, self.menu = None, {}, None
            return
        
    def send_message(self, msg, file=None, contact=None):
        if not self.whatsapp:
            # TODO: Custom exception
            raise Exception("Missing whatsapp interface object")

        options = {}

        if contact:
            options['contactCard'] = contact.id

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
    def update_database(self):
        database.update_user(self.phonenumber, self.name, self.permissions, self.menu)
    