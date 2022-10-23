from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.boxlayout import MDBoxLayout
from pwd_data import PwdItem
from kivy.properties import ObjectProperty
import config

class DlgSetPwdContent(MDBoxLayout):
    txt_password = ObjectProperty(None)
    txt_password_confirm = ObjectProperty(None)


class DlgSetPwd(MDDialog):
    """
    This window is the dialog to edit a single item of the list
    """

    def __init__(self, **kwargs):
        super(DlgSetPwd, self).__init__(**kwargs,
                                          title="Address:",
                                          type="custom",
                                          content_cls=DlgSetPwdContent(),
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

    def on_confirm(self, instance):
        print("confirm")
        if self.content_cls.txt_password.text == self.content_cls.txt_password_confirm.text:
            config.glbl_config.set_password(self.content_cls.txt_password.text)
            self.dismiss(force=True)
        else:
            print("wrong password")

    def on_cancel(self, instance):
        print("cancel")
        self.dismiss(force=True)

    def Content(self):
        pass




def DialogSetPassword(**kwargs):
    dlg = DlgSetPwd(**kwargs)
    dlg.open()




class DlgChkPwdContent(MDBoxLayout):
    txt_password = ObjectProperty(None)
    pass


class DlgChkPwd(MDDialog):
    """
    This window is the dialog to edit a single item of the list
    """

    def __init__(self, **kwargs):
        super(DlgChkPwd, self).__init__(**kwargs,
                                          title="Insert Password",
                                          type="custom",
                                          content_cls=DlgChkPwdContent(),
                                          buttons=[
                                              MDFlatButton(
                                                  text="OK",
                                                  theme_text_color="Custom",
                                                  on_release=self.on_confirm
                                              ),
                                          ])

        self.content_cls.txt_password.text = ""

    def on_confirm(self, instance):
        print("confirm")
        if self.content_cls.txt_password.text == config.glbl_config.password:
            self.dismiss(force=True)
        else:
            print("wrong password!!!!")

    def Content(self):
        pass


def DialogCheckPassword(**kwargs):
    dlg = DlgChkPwd(**kwargs)
    dlg.open()
