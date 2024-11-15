from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from classes.data_classes import ReturnData
    from utils.global_vars import GlobalVars

from classes.video_class import *
from classes.data_classes import *

from utils.convert import struct_to_time
from utils.translate import txt
from utils.save import update
from database.guild import guild

from time import time
import discord

def get_voice_client(iterable, **attrs) -> discord.VoiceClient:
    """
    Gets voice_client from voice_clients list
    :param iterable: list
    :return: discord.VoiceClient
    """
    from operator import attrgetter

    # noinspection PyShadowingNames
    def _get(iterable, /, **attrs):
        # global -> local
        _all = all
        attrget = attrgetter

        # Special case the single element call
        if len(attrs) == 1:
            k, v = attrs.popitem()
            pred = attrget(k.replace('__', '.'))
            return next((elem for elem in iterable if pred(elem) == v), None)

        converted = [(attrget(attr.replace('__', '.')), value) for attr, value in attrs.items()]
        for elem in iterable:
            if _all(pred(elem) == value for pred, value in converted):
                return elem
        return None

    # noinspection PyShadowingNames
    async def _aget(iterable, /, **attrs):
        # global -> local
        _all = all
        attrget = attrgetter

        # Special case the single element call
        if len(attrs) == 1:
            k, v = attrs.popitem()
            pred = attrget(k.replace('__', '.'))
            async for elem in iterable:
                if pred(elem) == v:
                    return elem
            return None

        converted = [(attrget(attr.replace('__', '.')), value) for attr, value in attrs.items()]

        async for elem in iterable:
            if _all(pred(elem) == value for pred, value in converted):
                return elem
        return None


    return (
        _aget(iterable, **attrs)  # type: ignore
        if hasattr(iterable, '__aiter__')  # isinstance(iterable, collections.abc.AsyncIterable) is too slow
        else _get(iterable, **attrs)  # type: ignore
    )

def create_embed(glob: GlobalVars, video, name: str, guild_id: int, embed_colour: (int, int, int) = (88, 101, 242)) -> discord.Embed:
    """
    Creates embed with video info
    :param video: VideoClass child
    :param glob: GlobalVars object
    :param name: str - title of embed
    :param guild_id: id of guild the embed is created for
    :param embed_colour: (int, int, int) - rgb colour of embed default: (88, 101, 242) -> #5865F2 == discord.Color.blurple()
    :return: discord.Embed
    """
    if video.radio_info is not None:
        return create_radio_embed(glob, video, name, guild_id, embed_colour)

    try:
        requested_by = f'{glob.bot.get_user(video.author['id']).mention}'
    except AttributeError:
        requested_by = video.author['name']

    title = video.title
    time_played = video.time(glob)
    author = f'[{video.channel_name}]({video.channel_link})'
    url = video.url
    thumbnail = video.picture

    started_at = struct_to_time(video.played_duration[0]["start"]["epoch"], "time")
    requested_at = struct_to_time(video.created_at, "time")

    # Create embed
    embed = (discord.Embed(title=name, description=f'```\n{title}\n```', color=discord.Color.from_rgb(*embed_colour)))

    embed.add_field(name=txt(guild_id, glob, 'Duration'), value=time_played)
    embed.add_field(name=txt(guild_id, glob, 'Requested by'), value=f"{requested_by}")
    embed.add_field(name=txt(guild_id, glob, 'Author'), value=author)

    embed.add_field(name=txt(guild_id, glob, 'URL'), value=url, inline=False)

    embed.set_thumbnail(url=thumbnail)
    embed.set_footer(text=f'{txt(guild_id, glob, "Requested at")} {requested_at} | {txt(guild_id, glob, "Started playing at")} {started_at}')

    return embed

def create_radio_embed(glob: GlobalVars, video, name: str, guild_id: int, embed_colour: (int, int, int) = (88, 101, 242)) -> discord.Embed:
    """
    Creates embed with radio info
    :param video: VideoClass child - Radio class
    :param glob: GlobalVars object
    :param name: str - title of embed
    :param guild_id: id of guild the embed is created for
    :param embed_colour: (int, int, int) - rgb colour of embed default: (88, 101, 242) -> #5865F2 == discord.Color.blurple()
    :return: discord.Embed
    """
    try:
        requested_by = f'{glob.bot.get_user(video.author['id']).mention}'
    except AttributeError:
        requested_by = video.author['name']

    ri: RadioInfoDict = video.radio_info
    radio_name = video.title
    time_played = video.time(glob)
    provider = f'[{video.channel_name}]({video.channel_link})'
    url = video.url
    thumbnail = video.picture

    started_at = struct_to_time(video.played_duration[0]["start"]["epoch"], "time")
    requested_at = struct_to_time(video.created_at, "time")

    # Check if there is now playing info
    if ri['now_title'] is not None:
        now_title = f"```{ri['now_title']}```" if ri['now_title'] is not None else '```Now Playing Title```'
        now_artist = f"```{ri['now_artist']}```" if ri['now_artist'] is not None else '```Now Playing Artist```'
        thumbnail = ri['now_picture'] if ri['now_picture'] is not None else thumbnail

        embed = discord.Embed(title=name, description=now_title+now_artist, color=discord.Color.from_rgb(*embed_colour))

        # embed.add_field(name=txt(guild_id, glob, 'Artist'), value=f'```{now_artist}```')
        embed.add_field(name=txt(guild_id, glob, 'Station'), value=f"[{radio_name}]({url})", inline=False)
        # embed.add_field(name='', value='', inline=False)

    else:
        embed = discord.Embed(title=name, description=f'```\n{radio_name}\n```', color=discord.Color.from_rgb(*embed_colour))


    embed.add_field(name=txt(guild_id, glob, 'Duration'), value=time_played)
    embed.add_field(name=txt(guild_id, glob, 'Requested by'), value=f"{requested_by}")
    embed.add_field(name=txt(guild_id, glob, 'Provider'), value=provider)

    embed.add_field(name=txt(guild_id, glob, 'URL'), value=url, inline=False)

    embed.set_thumbnail(url=thumbnail)
    embed.set_footer(text=f'{txt(guild_id, glob, "Requested at")} {requested_at} | {txt(guild_id, glob, "Started playing at")} {started_at}')

    return embed

def create_search_embed(glob: GlobalVars, video_info: VideoInfo, name: str, guild_id: int, embed_colour: (int, int, int) = (88, 101, 242)) -> discord.Embed:
    """
    Creates embed with search result
    :param glob: GlobalVars object
    :param video_info: VideoInfo
    :param name: str - title of embed
    :param guild_id: id of guild the embed is created for
    :param embed_colour: (int, int, int) - rgb colour of embed default: (88, 101, 242) -> #5865F2 == discord.Color.blurple()
    :return: discord.Embed
    """
    embed = discord.Embed(title=name, description=f'```\n{video_info["title"]}\n```', color=discord.Color.from_rgb(*embed_colour))

    embed.add_field(name=txt(guild_id, glob, 'Duration'), value=video_info['duration'])
    embed.add_field(name=txt(guild_id, glob, 'Author'), value=f"[{video_info['channel']['name']}]({video_info['channel']['link']})")

    embed.add_field(name=txt(guild_id, glob, 'URL'), value=video_info['link'])

    embed.set_thumbnail(url=video_info['thumbnails'][0]['url'])

    return embed

async def to_queue(glob: GlobalVars, guild_id: int or Guild, video, position: int = None, copy_video: bool=True, stream_strip: bool = True) -> ReturnData or None:
    """
    Adds video to queue

    if return_message is True returns: [bool, str, VideoClass child]

    :param glob: GlobalVars object
    :param guild_id: id of guild: int or Guild
    :param video: VideoClass child
    :param position: int - position in queue to add video
    :param copy_video: bool - if True copies video
    :param stream_strip: bool - if True strips video of stream_url
    :return: ReturnData or None
    """
    guild_object = guild(glob, guild_id)

    if copy_video:
        video = await to_queue_class(glob, video)

    # strip video of time data
    video.played_duration = [{'start': {'epoch': None, 'time_stamp': None}, 'end': {'epoch': None, 'time_stamp': None}}]
    # strip video of discord channel data
    video.discord_channel = {"id": None, "name": None}
    # set new creation date
    video.created_at = int(time())
    # strip video of subtitles
    video.subtitles = None
    # strip video of captions
    video.captions = None

    if stream_strip is True:
        video.stream_url = None

    queue_video = await to_queue_class(glob, video)

    if position is None:
        guild(glob, guild_id).queue.append(queue_video)
    else:
        guild(glob, guild_id).queue.insert(position, queue_video)

    update(glob)

    return f'[`{video.title}`](<{video.url}>) {txt(guild_id, glob, "added to queue!")} {glob.notif}'

def get_content_of_message(glob: GlobalVars, message: discord.Message) -> (str, list or None):
    """
    Returns content of message

    if message has attachments returns url of first attachment and list with filename, author and link of message

    if message has embeds returns str representation of first embed without thumbnail and None

    if message has embeds and content returns content of message and None

    :param glob: GlobalVars object
    :param message: message: discord.Message
    :return: content: str, probe_data: list or None
    """
    if message.attachments:
        url = message.attachments[0].url
        filename = message.attachments[0].filename
        message_author = f"Message by {get_username(glob, message.author.id)}"
        message_link = message.jump_url
        probe_data = [filename, message_author, message_link]
    elif message.embeds:
        if message.content:
            url = message.content
            probe_data = None
        else:
            embed = message.embeds[0]
            embed_dict = embed.to_dict()
            embed_dict.pop('thumbnail')
            embed_str = str(embed_dict)
            url = embed_str
            probe_data = None
    else:
        url = message.content
        probe_data = None

    return url, probe_data

def get_username(glob: GlobalVars, user_id: int) -> str:
    """
    Returns username of user_id with bot.get_user

    if can't find user returns str(user_id)

    :param glob: GlobalVars object
    :param user_id: id of user
    :return: str - username of user_id or str(user_id)
    """
    # noinspection PyBroadException
    try:
        return glob.bot.get_user(int(user_id)).name
    except Exception:
        return str(user_id)
