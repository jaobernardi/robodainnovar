from .. import database


class User():
    def __init__(self, phonenumber, id):
        self.phonenumber = phonenumber
        self.id = id
        self.fetch_database()
    

    def fetch_database(self):
        response = database.get_user(self.phonenumber)
        if not response:
            database.create_user(self.phonenumber)
            self.name, self.permissions, self.menu = None, {}, None
            return
        
        phonenumber, self.name, self.permissions, self.menu = response
    
    def update_database(self):
        database.update_user(self.phonenumber, self.name, self.permissions, self.menu)
    