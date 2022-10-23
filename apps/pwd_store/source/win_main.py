from kivymd.uix.boxlayout import MDBoxLayout
from ctrl_toolbar import PwdCTopToolbar, PwdCBotToolbar
from kivy.uix.scrollview import ScrollView
from pwd_data import PwdData, PwdGroup, PwdItem
from ctrl_elements import CtrlPwdItemList, CtrlPwdGroupList,CtrlPwdItem,CtrlPwdGroup
from kivy.uix.screenmanager import ScreenManager, Screen
from win_debug import WinDebug
from kivymd.app import MDApp

from config import Config
from dialog_password import DialogSetPassword, DialogCheckPassword
import config

glbl_screen_manager = ScreenManager()


class WinMain(Screen):

    def __init__(self, data_file_, **kwargs):
        super(WinMain, self).__init__(**kwargs, name="main")
        self.add_widget(WinMainLayout(data_file_))



class WinMainLayout(MDBoxLayout):

    pwd_data: PwdData

    def __init__(self, data_file_, **kwargs):
        super(WinMainLayout, self).__init__(**kwargs, orientation='vertical')

        self.pwd_data = data_file_
        # toolbar = Builder.load_string(md_tool_bar)

        #if config.glbl_config.passwd() == "":
        #    return DialogSetPassword(on_dismiss=self.init)
        #else:
        #    return DialogCheckPassword(on_dismiss=self.init)
        self.init(None)

    def init(self, instance):
        top_toolbar = PwdCTopToolbar()
        top_toolbar.add_btn_right('plus', self.on_add_item)
        top_toolbar.add_btn_right('account-multiple-plus', self.on_add_group)
        top_toolbar.add_btn_right('bug', self.on_debug)
        self.add_widget(top_toolbar)

        self.ctrl_pwd_item_list = CtrlPwdItemList(self.pwd_data)
        scroll_view_items = ScrollView(do_scroll_x=False, do_scroll_y=True)
        self.add_widget(scroll_view_items)
        scroll_view_items.add_widget(self.ctrl_pwd_item_list)

        self.ctrl_pwd_group_list = CtrlPwdGroupList(self.pwd_data)
        scroll_view_group = ScrollView(do_scroll_x=False, do_scroll_y=True,size_hint_y=0.33)
        self.add_widget(scroll_view_group)
        scroll_view_group.add_widget(self.ctrl_pwd_group_list)

        bottom_toolbar = PwdCBotToolbar(type_height="small")
        bottom_toolbar.add_btn_left('group', self.on_choose_group)
        self.add_widget(bottom_toolbar)

    def on_add_item(self):
        print("add item")
        item: PwdItem = self.pwd_data.add_item("item")
        self.ctrl_pwd_item_list.add_widget(CtrlPwdItem(self.ctrl_pwd_item_list, item))


    def on_add_group(self):
        print("add grp")
        grp: PwdGroup = self.pwd_data.add_group("group")
        self.ctrl_pwd_group_list.add_widget(CtrlPwdGroup(self.ctrl_pwd_group_list, grp))

    def on_choose_group(self):
        print("choose group")

    def on_debug(self):
        glbl_screen_manager.current = 'debug'
