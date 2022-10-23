import bcrypt
from kivymd.uix.dialog import MDDialog
from kivymd.uix.textfield import MDTextField



class FldEditPassword(MDTextField):

    def __init__(self, **kwargs):
        super(MDTextField, self).__init__(self, **kwargs, hint_text="insert password")

    def on_enter(self, instance, value):
        print('User pressed enter in', instance)

textinput = TextInput(text='Hello world', multiline=False)
textinput.bind(on_text_validate=on_enter)

def set_password():
    dialog = MDInputDialog(
        title='Title', hint_text='Hint text', size_hint=(.8, .4),
        text_button_ok='Yes',
        events_callback=self.callback_for_menu_items)
    dialog.open()

    # store your password:
    password = str(input("input password: "))

    # Encode the stored password:
    password = password.encode('utf-8')

    # Encrypt the stored password:
    hashed = bcrypt.hashpw(password, bcrypt.gensalt(10))


def crypt():

    # Create an authenticating password input field to check if a user enters the correct password
    check = str(input("check password: "))

    # Encode the authenticating password as well
    check = check.encode('utf-8')

    # Use conditions to compare the authenticating password with the stored one:
    if bcrypt.checkpw(check, hashed):
        print("login success")
    else:
        print("incorrect password")