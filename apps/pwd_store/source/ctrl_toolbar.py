from kivymd.uix.toolbar import MDTopAppBar, MDBottomAppBar
from kivymd.uix.menu import MDDropdownMenu
from kivy.metrics import dp
from kivy.app import App
from kivy.core.window import Window

class PwdCTopToolbar(MDTopAppBar):

    def __init__(self, **kwargs):
        super(PwdCTopToolbar, self).__init__(**kwargs, title="PwdMan")
        self.left_action_items = [['menu', lambda x: self.navigation_draw(x)]]
        d_items = ["pippo", "pluto", "paperino"]
        menu_items = [
            {
                "viewclass": "OneLineListItem",
                "text": i,
                "height": dp(40),
                "on_release": lambda x=i: self.menu_callback(self.menu,x),
            } for i in d_items
        ]
        self.menu = MDDropdownMenu(items=menu_items, width_mult=4)
        self.menu.bind(on_release=self.menu_callback)

    def add_btn_left(self, ico_, callback_):
        self.left_action_items.append([ico_, lambda x: callback_()])

    def add_btn_right(self, ico_, callback_):
        self.right_action_items.append([ico_, lambda x: callback_()])

    def navigation_draw(self, button):
        self.menu.caller = button
        self.menu.open()

    def menu_callback(self, menu, item):
        print("item clicked")


class PwdCBotToolbar(MDTopAppBar):

    def __init__(self, **kwargs):
        super(PwdCBotToolbar, self).__init__(**kwargs)
        self.right_action_items = [['logout', lambda x: self.close_application(x)]]

    def add_btn_left(self, ico_, callback_):
        self.left_action_items.append([ico_, lambda x: callback_(x)])

    def add_btn_right(self, ico_, callback_):
        self.right_action_items.append([ico_, lambda x: callback_(x)])

    def close_application(self, _button):
        print("close application")
        App.get_running_app().stop()    # closing application
        Window.close()                  # removing window
