import os
import json
from dotenv import load_dotenv

load_dotenv()

def get_env(_key: str, var_type: type=str, default=None):
    _value = os.getenv(_key)
    if _value is None:
        return default

    try:
        return var_type(_value)
    except ValueError:
        return _value

CLIENT_ID = get_env('CLIENT_ID', int)
OWNER_ID = get_env('OWNER_ID', int, 349164237605568513)
BOT_TOKEN = get_env('BOT_TOKEN')
CLIENT_SECRET = get_env('CLIENT_SECRET')
PREFIX = get_env('PREFIX')
NOTIF = get_env('NOTIF')
SPOTIFY_CLIENT_ID = get_env('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = get_env('SPOTIFY_CLIENT_SECRET')
SPOTIFY_REDIRECT_URI = get_env('SPOTIFY_REDIRECT_URI')
SOUNDCLOUD_CLIENT_ID = get_env('SOUNDCLOUD_CLIENT_ID')
DEFAULT_DISCORD_AVATAR = get_env('DEFAULT_DISCORD_AVATAR')
VLC_LOGO = get_env('VLC_LOGO')
DEVELOPER_ID = get_env('DEVELOPER_ID', int, 349164237605568513)
INVITE_URL = get_env('INVITE_URL')

try:
    AUTHORIZED_USERS = json.loads(os.environ.get('AUTHORIZED_USERS', '[]'))
    AUTHORIZED_USERS = [int(user) for user in AUTHORIZED_USERS]
except json.JSONDecodeError:
    AUTHORIZED_USERS = []
except ValueError:
    pass
