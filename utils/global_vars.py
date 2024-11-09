from utils.log import log

import json

class GlobalVars:
    def __init__(self, bot_var, ses_var, sp_var, sc_var, notif):
        """
        Global variables class
        :param bot_var: Bot object
        :param ses_var: Session object
        :param sp_var: Spotipy object
        :param sc_var: SoundCloud object
        """
        self.bot = bot_var
        self.ses = ses_var
        self.sp = sp_var
        self.sc = sc_var
        self.notif = notif


try:
    with open(f'json/radios.json', 'r', encoding='utf-8') as file:
        radio_dict = json.load(file)
except Exception as e:
    log(None, f"Error loading radio_dict: {e}", log_type="error")
    with open(f'json/radio.json', 'w', encoding='utf-8') as file:
        radio_dict = json.load(file)

with open(f'json/languages.json', 'r', encoding='utf-8') as file:
    languages_dict = json.load(file)

with open(f'json/languages_shortcuts.json', 'r', encoding='utf-8') as file:
    languages_shortcuts_dict = json.load(file)

with open(f'json/languages_list.json', 'r', encoding='utf-8') as file:
    languages_list_dict = json.load(file)
