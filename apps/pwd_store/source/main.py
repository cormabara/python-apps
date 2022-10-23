"""
Gestire colore di background
md_bg_color=(0.000, 1.000, 0.498, 1)s
"""
from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager
from pwd_data import PwdData
from win_main import WinMain
from win_debug import WinDebug
from kivy.logger import Logger
from kivy.lang import Builder
import config
import win_main


# Configuration file for the application
DATA_FILE = "./datafile.json"
from kivy.core.window import Window
Window.softinput_mode = 'below_target'



class AppManager:

    data_file: PwdData

    def __init__(self):
        self.data_file = PwdData()

    def load(self):
        config.glbl_config.load()
        self.data_file.load(DATA_FILE)

    def save(self):
        config.glbl_config.save()
        self.data_file.save()


class PwdManager(MDApp):

    def build(self):
        self.theme_cls.theme_style = "Dark"
        # Builder.load_string(MyLayout)
        win_main.glbl_screen_manager.add_widget(WinMain(app_manager.data_file))
        win_main.glbl_screen_manager.add_widget(WinDebug())
        Builder.load_file("my_layout.kv")
        return win_main.glbl_screen_manager


if __name__ == "__main__":
    Logger.debug("Launching Pwd Manager")
    app_manager = AppManager()
    app_manager.load()
    PwdManager().run()
    print("closing application")
    app_manager.save()
