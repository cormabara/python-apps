from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.boxlayout import MDBoxLayout
from pwd_data import PwdItem
from kivy.properties import ObjectProperty


class WinEditItemContent(MDBoxLayout):
    txt_name = ObjectProperty(None)
    txt_user = ObjectProperty(None)
    txt_password = ObjectProperty(None)
    txt_notes = ObjectProperty(None)


class WinEditItem(MDDialog):
    """
    This window is the dialog to edit a single item of the list
    """

    def __init__(self, pwd_item_: PwdItem, **kwargs):
        super(WinEditItem, self).__init__(**kwargs,
                                          title="Address:",
                                          type="custom",
                                          content_cls=WinEditItemContent(),
                                          buttons=[
                                              MDFlatButton(
                                                  text="CANCEL",
                                                  theme_text_color="Custom",
                                                  on_release=self.on_cancel
                                              ),
                                              MDFlatButton(
                                                  text="OK",
                                                  theme_text_color="Custom",
                                                  on_release=self.on_confirm
                                              ),
                                          ])

        self.pwd_item = pwd_item_
        self.content_cls.txt_name.text = self.pwd_item.name
        self.content_cls.txt_user.text = self.pwd_item.user
        self.content_cls.txt_password.text = self.pwd_item.password
        self.content_cls.txt_notes.text = self.pwd_item.notes

    def on_confirm(self, instance):
        print("confirm")
        self.pwd_item.set_name(self.content_cls.txt_name.text)
        self.pwd_item.set_user(self.content_cls.txt_user.text)
        self.pwd_item.set_password(self.content_cls.txt_password.text)
        self.pwd_item.set_notes(self.content_cls.txt_notes.text)
        self.dismiss(force=True)

    def on_cancel(self, instance):
        print("cancel")
        self.dismiss(force=True)

    def Content(self):
        pass


def DialogEditItem(pwd_item_: PwdItem, **kwargs):
    dlg = WinEditItem(pwd_item_,**kwargs)
    dlg.open()


