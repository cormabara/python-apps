import json
import os


class Config:

    password: str
    FILENAME = "config.json"

    def __init__(self):
        self.password = ""
        pass

    def from_json(self, obj_: object):
        self.password = obj_['main_password']
        return self

    def to_json(self):
        obj = dict()
        obj['main_password'] = self.password
        return obj

    def set_password(self, pwd_):
        self.password = pwd_

    def passwd(self):
        return self.password

    def load(self):
        # if file not exist save it
        if not os.path.exists(self.FILENAME):
            self.save()
            return False

        try:
            with open(self.FILENAME, "r") as read_file:
                json_obj = json.load(read_file)
                self.from_json(json_obj)
        except Exception as exc_:
            print("Exception on load data: " + self.FILENAME)
            print(exc_)
            return False

        return True

    def save(self):
        try:
            with open(self.FILENAME, "w") as write_file:
                json_obj = self.to_json()
                json.dump(json_obj, write_file, indent=3)
                return True
        except Exception as exc_:
            print("Exception on save data")
            print(exc_)
            return False


glbl_config = Config()
