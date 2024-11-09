
from utils.global_vars import GlobalVars

import classes.data_classes as data_classes
import classes.video_class as video_class

from flask_sqlalchemy import SQLAlchemy

def get_session(glob: GlobalVars or SQLAlchemy):
    if isinstance(glob, GlobalVars):
        return glob.ses
    elif isinstance(glob, SQLAlchemy):
        return glob.session
    else:
        raise TypeError("glob must be either GlobalVars or SQLAlchemy")

def guild(glob: GlobalVars or SQLAlchemy, guild_id: int or data_classes.Guild) -> data_classes.Guild:
    """
    Returns a guild object
    :param glob: GlobalVars or SQLAlchemy
    :param guild_id: ID of the guild or Guild object
    :return: Guild object
    """
    if isinstance(guild_id, data_classes.Guild):
        return guild_id

    session = get_session(glob)
    with session.no_autoflush:
        return session.query(data_classes.Guild).filter_by(id=int(guild_id)).first()

def guilds(glob: GlobalVars or SQLAlchemy) -> list[data_classes.Guild]:
    """
    Returns a list of guild objects
    :param glob: GlobalVars or SQLAlchemy
    :return: [Guild object, ...]
    """
    session = get_session(glob)
    with session.no_autoflush:
        return session.query(data_classes.Guild).all()

def guild_data(glob: GlobalVars or SQLAlchemy, guild_id: int) -> data_classes.GuildData:
    """
    Returns a guild data object
    :param glob: GlobalVars or SQLAlchemy
    :param guild_id: ID of the guild
    :return: GuildData object
    """
    session = get_session(glob)
    with session.no_autoflush:
        return session.query(data_classes.GuildData).filter_by(id=int(guild_id)).first()

def guild_exists(glob: GlobalVars or SQLAlchemy, guild_id: int) -> bool:
    """
    Returns whether or not a guild exists
    :param glob: GlobalVars or SQLAlchemy
    :param guild_id: ID of the guild
    :return: bool
    """
    session = get_session(glob)
    with session.no_autoflush:
        return session.query(data_classes.Guild).filter_by(id=guild_id).first() is not None

def guild_dict(glob: GlobalVars or SQLAlchemy) -> dict[int, data_classes.Guild]:
    """
    Returns a dictionary of guild objects
    :param glob: GlobalVars or SQLAlchemy
    :return: {guild_id: Guild object, ...}
    """
    session = get_session(glob)
    with session.no_autoflush:
        _guilds = {}
        for guild_object in session.query(data_classes.Guild).all():
            _guilds[guild_object.id] = guild_object
        return _guilds

def guild_ids(glob: GlobalVars or SQLAlchemy) -> list[int]:
    """
    Returns a list of guild IDs
    :param glob: GlobalVars or SQLAlchemy
    :return: [guild_id, ...]
    """
    session = get_session(glob)
    with session.no_autoflush:
        _guilds = []
        for guild_object in session.query(data_classes.Guild).all():
            _guilds.append(guild_object.id)
        return _guilds

# Guild variables
def guild_last_updated(glob: GlobalVars or SQLAlchemy, guild_id: int) -> int or None:
    """
    Returns the last updated time of the guild
    :param glob: GlobalVars or SQLAlchemy
    :param guild_id: ID of the guild
    :return: int or None
    """
    session = get_session(glob)
    with session.no_autoflush:
        result = session.query(data_classes.Guild).filter_by(id=guild_id).with_entities(data_classes.Guild.last_updated).first()
        return result[0] if result is not None else None
# noinspection DuplicatedCode
def guild_options_loop(glob: GlobalVars or SQLAlchemy, guild_id: int) -> bool:
    """
    Returns the loop of the guild
    :param glob: GlobalVars or SQLAlchemy
    :param guild_id: ID of the guild
    :return: bool
    """
    session = get_session(glob)
    with session.no_autoflush:
        result = session.query(data_classes.Options).filter_by(id=guild_id).with_entities(data_classes.Options.loop).first()
        return result[0] if result is not None else None
# noinspection DuplicatedCode
def guild_options_buffer(glob: GlobalVars or SQLAlchemy, guild_id: int) -> int:
    """
    Returns the buffer of the guild
    :param glob: GlobalVars or SQLAlchemy
    :param guild_id: ID of the guild
    :return: int
    """
    session = get_session(glob)
    with session.no_autoflush:
        result = session.query(data_classes.Options).filter_by(id=guild_id).with_entities(data_classes.Options.buffer).first()
        return result[0] if result is not None else None
# noinspection DuplicatedCode
def guild_options_response_type(glob: GlobalVars or SQLAlchemy, guild_id: int) -> str:
    """
    Returns the response type of the guild
    :param glob: GlobalVars or SQLAlchemy
    :param guild_id: ID of the guild
    :return: str
    """
    session = get_session(glob)
    with session.no_autoflush:
        result = session.query(data_classes.Options).filter_by(id=guild_id).with_entities(data_classes.Options.response_type).first()
        return result[0] if result is not None else None
# noinspection DuplicatedCode
def guild_options_language(glob: GlobalVars or SQLAlchemy, guild_id: int) -> str:
    """
    Returns the language of the guild
    :param glob: GlobalVars or SQLAlchemy
    :param guild_id: ID of the guild
    :return: str
    """
    session = get_session(glob)
    with session.no_autoflush:
        result = session.query(data_classes.Options).filter_by(id=guild_id).with_entities(data_classes.Options.language).first()
        return result[0] if result is not None else None
# noinspection DuplicatedCode
def guild_options_is_radio(glob: GlobalVars or SQLAlchemy, guild_id: int) -> bool:
    """
    Returns whether or not the guild is a radio
    :param glob: GlobalVars or SQLAlchemy
    :param guild_id: ID of the guild
    :return: bool
    """
    session = get_session(glob)
    with session.no_autoflush:
        result = session.query(data_classes.Options).filter_by(id=guild_id).with_entities(data_classes.Options.is_radio).first()
        return result[0] if result is not None else None
# noinspection DuplicatedCode
def guild_options_volume(glob: GlobalVars or SQLAlchemy, guild_id: int) -> float:
    """
    Returns the volume of the guild
    :param glob: GlobalVars or SQLAlchemy
    :param guild_id: ID of the guild
    :return: float
    """
    session = get_session(glob)
    with session.no_autoflush:
        result = session.query(data_classes.Options).filter_by(id=guild_id).with_entities(data_classes.Options.volume).first()
        return result[0] if result is not None else None
# noinspection DuplicatedCode
def guild_options_buttons(glob: GlobalVars or SQLAlchemy, guild_id: int) -> bool:
    """
    Returns the buttons of the guild
    :param glob: GlobalVars or SQLAlchemy
    :param guild_id: ID of the guild
    :return: bool
    """
    session = get_session(glob)
    with session.no_autoflush:
        result = session.query(data_classes.Options).filter_by(id=guild_id).with_entities(data_classes.Options.buttons).first()
        return result[0] if result is not None else None

# Guild Commands
def create_guild(glob: GlobalVars or SQLAlchemy, guild_id: int) -> None:
    """
    Creates a guild object
    :param glob: GlobalVars or SQLAlchemy
    :param guild_id: ID of the guild
    :return: Guild object
    """
    session = get_session(glob)
    with session.no_autoflush:
        guild_object = data_classes.Guild(glob, guild_id, {})
        session.add(guild_object)
        session.commit()
def delete_guild(glob: GlobalVars or SQLAlchemy, guild_id: int) -> None:
    """
    Deletes a guild object
    :param glob: GlobalVars or SQLAlchemy
    :param guild_id: ID of the guild
    :return: None
    """
    session = get_session(glob)
    with session.no_autoflush:
        session.query(data_classes.Guild).filter_by(id=guild_id).delete()
        session.query(data_classes.GuildData).filter_by(id=guild_id).delete()
        session.query(data_classes.Options).filter_by(id=guild_id).delete()

        session.query(video_class.Queue).filter_by(guild_id=guild_id).delete()
        session.query(video_class.NowPlaying).filter_by(guild_id=guild_id).delete()

        session.commit()

# Queue
def guild_queue(glob: GlobalVars or SQLAlchemy, guild_id: int):
    """
    Returns a list of videos in the queue
    :param glob: GlobalVars or SQLAlchemy
    :param guild_id: ID of the guild
    :return: [Queue object, ...]
    """
    session = get_session(glob)
    with session.no_autoflush:
        return session.query(video_class.Queue).filter_by(guild_id=guild_id).all()

def clear_queue(glob: GlobalVars or SQLAlchemy, guild_id: int) -> int:
    """
    Clears the queue
    :param glob: GlobalVars or SQLAlchemy
    :param guild_id: ID of the guild
    :return: int - number of videos deleted
    """
    session = get_session(glob)
    with session.no_autoflush:
        query = session.query(video_class.Queue).filter_by(guild_id=guild_id)
        query_count = query.count()
        query.delete()
        session.commit()
        return query_count