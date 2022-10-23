from kivy.uix.screenmanager import Screen
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.textinput import TextInput


class WinDebug(Screen):
    def __init__(self, **kwargs):
        super(WinDebug, self).__init__(**kwargs, name="debug")
        self.add_widget(DebugLayout())


class DebugLayout(MDBoxLayout):

    def __init__(self, **kwargs):
        super(DebugLayout, self).__init__(**kwargs)

        self.add_widget(TextInput())