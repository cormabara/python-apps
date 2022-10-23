from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDIconButton
from kivymd.uix.list import MDList
from pwd_data import PwdData, PwdGroup, PwdItem
from dialog_edit_item import DialogEditItem


class LblItem(MDLabel):
    pass
#    def __init__(self, master_, **kwargs):
#        super(LblItem, self).__init__(**kwargs)
#        self.master = master_


class BtnItem(MDIconButton):

    def __init__(self, master_, **kwargs):
        super(BtnItem, self).__init__(**kwargs)
        self.master = master_



class CtrlPwdElement(MDBoxLayout):

    def __init__(self, master_, **kwargs):
        super(CtrlPwdElement, self).__init__(**kwargs, orientation='horizontal', adaptive_height=True)
        self.master = master_
        int_box = MDBoxLayout(size_hint_x=0.8, size_hint_y=0.8, orientation='horizontal', md_bg_color=(36/255, 38/255, 45/255, 0.8))
        self.add_widget(int_box)
        self.btn_edit = BtnItem(self, icon="pencil", pos_hint={"center_x": .5, "center_y": .5})
        int_box.add_widget(self.btn_edit)
        self.lbl_name = LblItem()
        int_box.add_widget(self.lbl_name)
        self.btn_delete = BtnItem(self,icon="delete", pos_hint={"center_x": .5, "center_y": .5})
        int_box.add_widget(self.btn_delete)


class CtrlPwdItem(CtrlPwdElement):

    pwd_item: PwdItem

    def __init__(self, master_, pwd_item_, **kwargs):
        super(CtrlPwdItem, self).__init__(master_, **kwargs)
        self.pwd_item = pwd_item_
        self.lbl_name.text = self.pwd_item.name
        self.btn_edit.bind(on_press=self.on_edit)
        self.btn_delete.bind(on_press=self.on_delete)
        self.bind(on_release=self.on_select)

    def on_delete(self, instance):
        self.master.on_delete_item(instance.master)

    def on_edit(self, instance):
        DialogEditItem(self.pwd_item, on_dismiss=self.refresh)

    def on_select(self, instance):
        print("selected")

    def refresh(self, instance):
        self.lbl_name.text = self.pwd_item.name


class CtrlPwdGroup(CtrlPwdElement):
    pwd_group: PwdGroup

    def __init__(self, master_, group_, **kwargs):
        super(CtrlPwdGroup, self).__init__(master_, **kwargs)
        self.master = master_
        self.pwd_group = group_
        self.lbl_name.text = self.pwd_group.name
        self.btn_edit.bind(on_press=self.on_edit)
        self.btn_delete.bind(on_press=self.on_delete)
        self.bind(on_release=self.on_select)

    def on_delete(self, instance):
        self.master.delete_group(instance.master)

    def on_edit(self, instance):
        print("edit")
        print(str(self.pwd_group))

    def on_select(self, instance):
        print("group selected")
        # print("grp " + str(self.pwd_group.name) + " selected")

class CtrlPwdItemList(MDList):

    pwd_data: PwdData

    def __init__(self, pwd_data_, **kwargs):
        super(CtrlPwdItemList, self).__init__(**kwargs)
        self.pwd_data = pwd_data_
        self.init_data(pwd_data_)

    def init_data(self, pwd_data_: PwdData):
        for dd in pwd_data_.item_list_get():
            self.add_widget(CtrlPwdItem(self,dd))

    def on_delete_item(self, wdgitem_: CtrlPwdItem):
        self.pwd_data.item_list_get().remove(wdgitem_.pwd_item)
        self.remove_widget(wdgitem_)

    def on_new_item(self, instance):
        item: PwdItem = self.pwd_data.add_item("item")
        self.add_widget(CtrlPwdItem(item))


class CtrlPwdGroupList(MDList):

    pwd_data: PwdData

    def __init__(self, pwd_data_, **kwargs):
        super(CtrlPwdGroupList, self).__init__(**kwargs)
        self.pwd_data = pwd_data_
        self.init_data(pwd_data_)

    def init_data(self, pwd_data_: PwdData):
        for dd in pwd_data_.groups:
            self.add_widget(CtrlPwdGroup(self,dd))

    def add_group(self, name_):
        grp: PwdGroup = self.pwd_data.groups.remove("item")
        self.add_widget(CtrlPwdGroup(grp))
        return grp

    def delete_group(self, wdg_group_: CtrlPwdGroup):
        self.pwd_data.groups.remove(wdg_group_.pwd_group)
        self.remove_widget(wdg_group_)

    def on_new_group(self, instance):
        grp: PwdGroup = self.pwd_data.add_group("item")
        self.add_widget(CtrlPwdGroup(grp))


