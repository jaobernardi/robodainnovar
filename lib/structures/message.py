from base64 import b64encode
from curses.ascii import US
import mimetypes
import os
from .user import User

class Message():
    def __init__(self, whatsapp, api_return):
        self.__dict__.update(api_return['message'])
        self.user = User(**api_return['user'])
        self.whatsapp = whatsapp
    
    def seen(self):
        self.whatsapp.seen_message(self.chatID)
    
    def reply(self, msg, qoute=True, file=None):
        options = {}
        if qoute:
            options["quotedMessageId"] = self.id
        
        if file:
            file = os.path.abspath(file)
            with open(file, "rb") as f:
                data = b64encode(f.read())
            options['attachment'] = {
                "data": data.decode("utf-8"),
                "mimetype": mimetypes.guess_type(os.path.abspath(file))[0],
                "filename": os.path.basename(file)
            }

        self.whatsapp.send_message(self.chatID, msg, options)