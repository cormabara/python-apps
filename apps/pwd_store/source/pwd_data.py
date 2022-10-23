import json
import os.path
from datetime import datetime

class PwdTimeStats:

    creation_date: datetime
    lastmod_date: datetime

    def __init__(self):
        self.creation_date = datetime.now()
        self.lastmod_date = datetime.now()
        self.date_format = "%m/%d/%Y, %H:%M:%S"

    def from_json(self, obj_: object):
        self.lastmod_date = datetime.strptime(obj_['last_modification'], self.date_format)
        self.creation_date = datetime.strptime(obj_['creation'], self.date_format)

    def to_json(self):
        obj = dict()
        obj['last_modification'] = self.lastmod_date.strftime(self.date_format)
        obj['creation'] = self.creation_date.strftime(self.date_format)
        return obj

    def update_last_mod(self):
        self.lastmod_date = datetime.now()

class PwdGroup:

    name: str
    time_stats: PwdTimeStats

    def __init__(self, name_):
        self.name = name_
        self.time_stats = PwdTimeStats()

    def from_json(self, obj_: object):
        self.name = obj_['name']
        # self.time_stats.from_json(obj_['time_stats'])
        return self

    def to_json(self):
        obj = dict()
        obj['name'] = self.name
        obj['time_stats'] = self.time_stats.to_json()
        return obj


class PwdItem:

    name: str
    user: str
    password: str
    mail: str
    time_stats: PwdTimeStats
    grp_name: str

    def __init__(self, name_):
        self.name = name_
        self.user = ""
        self.password = ""
        self.mail = ""
        self.grp_name = ""
        self.notes = ""
        self.time_stats = PwdTimeStats()

    def set_name(self, v_):
        self.name = v_

    def set_user(self, v_):
        self.user = v_

    def set_password(self, v_):
        self.password = v_

    def set_mail(self, v_):
        self.mail = v_

    def set_notes(self, v_):
        self.notes = v_

    def from_json(self, obj_: object):
        self.name = obj_['name']
        self.grp_name = obj_['grp_name']
        self.user = obj_['user']
        self.password = obj_['password']
        self.mail = obj_['mail']
        self.notes = obj_['notes']
        self.time_stats.from_json(obj_['time_stats'])
        return self

    def to_json(self):
        obj = dict()
        obj['name'] = self.name
        obj['user'] = self.user
        obj['password'] = self.password
        obj['mail'] = self.mail
        obj['notes'] = self.notes
        obj['grp_name'] = self.grp_name
        obj['time_stats'] = self.time_stats.to_json()
        return obj


class PwdData:

    time_stats: PwdTimeStats
    item_list: list
    groups: list

    def __init__(self, fn_=None):
        self.to_save = False
        self.item_list: PwdItem = []
        self.groups: PwdGroup = []
        self.time_stats = PwdTimeStats()
        if fn_ is not None:
            if not self.load():
                self.creation_date = datetime.now()
                self.to_save = True

            self.datafile = fn_


    def grp_list_get(self):
        return self.groups

    def item_list_get(self):
        return self.item_list

    def get_items_by_group(self, grp_name_):
        ret_list = []
        for it in self.item_list:
            if it.grp_name == grp_name_:
                ret_list.append(it)

        return ret_list

    def from_json(self, obj_: object):
        self.time_stats.from_json(obj_['time_stats'])
        self.item_list = [PwdItem("null").from_json(s_obj['pwd_item']) for s_obj in obj_["pwd_items"]]
        self.groups = [PwdGroup("").from_json(s_obj['grp']) for s_obj in obj_["groups"]]
        print(self.item_list)

    def to_json(self):
        obj = dict()
        obj['time_stats'] = self.time_stats.to_json()
        obj['pwd_items'] = ([{"pwd_item": it.to_json()} for it in self.item_list])
        obj['groups'] = ([{"grp": grp.to_json()} for grp in self.groups])
        return obj

    def load(self, fn_):
        self.datafile = fn_

        # if file not exist save it
        if not os.path.exists(fn_):
            self.save()
            return False

        try:
            with open(fn_, "r") as read_file:
                json_obj = json.load(read_file)
                self.from_json(json_obj)
        except Exception as exc_:
            print("Exception on load data: " + fn_)
            print(exc_)
            return False

        self.datafile = fn_
        return True

    def save(self):
        self.time_stats.update_last_mod()

        try:
            with open(self.datafile, "w") as write_file:
                json_obj = self.to_json()
                json.dump(json_obj, write_file, indent=3)
                return True
        except Exception as exc_:
            print("Exception on save data")
            print(exc_)
            return False

    def add_item(self, name_):
        item = PwdItem(name_)
        self.item_list.append(item)
        return item

    def add_group(self, name_):
        grp = PwdGroup(name_)
        self.groups.append(grp)
        return grp
