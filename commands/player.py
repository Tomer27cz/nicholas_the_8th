from turtledemo.penrose import start

from classes.video_class import Queue
from classes.data_classes import ReturnData


from database.guild import guild, clear_queue

from utils.source import GetSource
from utils.log import log
from utils.translate import txt
from utils.save import update
from utils.discord import create_embed, to_queue
from utils.video_time import set_started, set_new_time
from utils.global_vars import GlobalVars

import classes.view
import commands.voice
import commands.queue
import commands.autocomplete

import asyncio
import random

from time import time

async def play_def(ctx, glob: GlobalVars,
                   url=None,
                   force: bool=False,
                   mute_response: bool=False,
                   after: bool=False,
                   no_search: bool=False,
                   embed: bool=None,
                   radio: bool=None,
                   player_id: int=None,
                   no_after: bool=None
                   ) -> ReturnData:
    log(ctx, 'play_def', options=locals(), log_type='function', author=ctx.author)
    guild_id, guild_object = ctx.guild.id, ctx.guild

    db_guild = guild(glob, guild_id)
    if not ctx.interaction.response.is_done():
        await ctx.defer()

    response = ReturnData(False, txt(guild_id, glob, 'Unknown error'))

    if after and db_guild.options.stopped or after and player_id != db_guild.options.player_id or after and no_after is True:
        log(ctx, f"play_def -> loop stopped (stopped: {db_guild.options.stopped}, id: {player_id}, db_id: {db_guild.options.player_id}, no_after: {no_after})", log_type='function')
        return ReturnData(False, txt(guild_id, glob, "Stopped play next loop"))

    voice = guild_object.voice_client
    if not voice:
        if ctx.author.voice is None:
            message = txt(guild_id, glob, "You are **not connected** to a voice channel")
            if not mute_response:
                await ctx.reply(message)
            return ReturnData(False, message)

    if url:
        # if voice:
        #     force = True if voice.is_playing() else force

        position = 0 if force else None
        response = await commands.queue.queue_command_def(ctx, glob, url=url, position=position, mute_response=True, force=force, from_play=True, no_search=no_search)

        if not response or not response.response:
            if not mute_response:
                if response is None:
                    return ReturnData(False, 'terminated')

                if response.terminate:
                    return ReturnData(False, 'terminated')

                await ctx.reply(response.message)
            return response

    if not guild_object.voice_client:
        join_response = await commands.voice.join_def(ctx, glob, None, True)
        voice = guild_object.voice_client
        if not join_response.response:
            if not mute_response:
                await ctx.reply(join_response.message)
            return join_response

    if voice.is_playing():
        if not force:
            if url:
                if response.video is not None:
                    message = f'{txt(guild_id, glob, "**Already playing**, added to queue")}: [`{response.video.title}`](<{response.video.url}>) {glob.notif}'
                    if not mute_response:
                        await ctx.reply(message)
                    return ReturnData(False, message)

                message = f'{txt(guild_id, glob, "**Already playing**, added to queue")} {glob.notif}'
                if not mute_response:
                    await ctx.reply(message)
                return ReturnData(False, message)

            message = f'{txt(guild_id, glob, "**Already playing**")} {glob.notif}'
            if not mute_response:
                await ctx.reply(message)
            return ReturnData(False, message)

        voice.stop()

    if voice.is_paused():
        return await commands.voice.resume_def(ctx, glob)

    if not db_guild.queue:
        message = f'{txt(guild_id, glob, "There is **nothing** in your **queue**")} {glob.notif}'
        if not after and not mute_response:
            await ctx.reply(message)
        return ReturnData(False, message)

    db_guild = guild(glob, guild_id)
    video = db_guild.queue[0]

    stream_url = video.url
    if video.class_type in ['RadioCz', 'RadioGarden', 'RadioTuneIn']:
        stream_url = video.radio_info['stream']
        embed = True if embed is None else embed

    elif video.class_type in ['Video', 'Probe', 'SoundCloud']:
        pass

    else:
        message = txt(guild_id, glob, "Unknown type")
        if not mute_response:
            await ctx.reply(message)
        return ReturnData(False, message)

    if not force:
        db_guild.options.stopped = False
        glob.ses.commit()

    # Set new player id
    p_id = player_id if player_id else random.choice([i for i in range(0, 9) if i not in [db_guild.options.player_id]])
    db_guild.options.player_id = p_id

    try:
        source, additional_data = await GetSource.create_source(glob, guild_id, stream_url, source_type=video.class_type, video_class=video)
        voice.play(source, after=lambda e: asyncio.run_coroutine_threadsafe(play_def(ctx, glob, after=True, player_id=p_id, no_after=no_after), glob.bot.loop))

        await commands.voice.volume_command_def(ctx, glob, db_guild.options.volume * 100, False, True)

        db_guild.options.stopped = False
        await set_started(glob, video, guild_object)

        glob.ses.query(Queue).filter_by(id=video.id).delete()
        glob.ses.commit()
        update(glob)

        # Response
        options = db_guild.options
        response_type = options.response_type

        message = f'{txt(guild_id, glob, "Now playing")} [`{video.title}`](<{video.url}>) {glob.notif}'
        view = classes.view.PlayerControlView(ctx, glob) # TODO: creating view here is not necessary (it's not used)

        if response_type == 'long' or embed:
            if not mute_response:
                embed = create_embed(glob, video, txt(guild_id, glob, "Now playing"), guild_id)
                if options.buttons:
                    view.message = await ctx.reply(embed=embed, view=view)
                else:
                    await ctx.reply(embed=embed)
            return ReturnData(True, message)

        elif response_type == 'short':
            if not mute_response:
                if options.buttons:
                    view.message = await ctx.reply(message, view=view)
                else:
                    await ctx.reply(message)
            return ReturnData(True, message)

        else:
            return ReturnData(True, message)

    except ConnectionRefusedError as e:
        await ctx.reply(e)
        return ReturnData(False, e)

async def now_def(ctx, glob: GlobalVars, ephemeral: bool = False) -> ReturnData:
    """
    Show now playing song
    :param ctx: Context
    :param glob: GlobalVars
    :param ephemeral: Should bot response be ephemeral
    :return: ReturnData
    """
    log(ctx, 'now_def', options=locals(), log_type='function', author=ctx.author)

    guild_id = ctx.guild.id
    db_guild = guild(glob, guild_id)

    if not ctx.interaction.response.is_done():
        await ctx.defer(ephemeral=ephemeral)

    if ctx.voice_client:
        if ctx.voice_client.is_playing():
            await db_guild.now_playing.renew(glob, force=True)
            embed = create_embed(glob, db_guild.now_playing, txt(guild_id, glob, "Now playing"), guild_id)

            view = classes.view.PlayerControlView(ctx, glob)

            if db_guild.options.buttons:
                view.message = await ctx.reply(embed=embed, view=view, ephemeral=ephemeral)
                return ReturnData(True, txt(guild_id, glob, "Now playing"))

            await ctx.reply(embed=embed, ephemeral=ephemeral)
            return ReturnData(True, txt(guild_id, glob, "Now playing"))

        if ctx.voice_client.is_paused():
            message = f'{txt(guild_id, glob, "There is no song playing right **now**, but there is one **paused:**")} [`{db_guild.now_playing.title}`](<{db_guild.now_playing.url}>) {glob.notif}'
            await ctx.reply(message, ephemeral=ephemeral)
            return ReturnData(False, message)

    message = txt(guild_id, glob, 'There is no song playing right **now**') + f" {glob.notif}"
    await ctx.reply(message, ephemeral=ephemeral)
    return ReturnData(False, message)

async def loop_command_def(ctx, glob: GlobalVars, clear_queue_opt: bool=False, ephemeral: bool=False) -> ReturnData:
    """
    Loop command
    :param ctx: Context
    :param glob: GlobalVars
    :param clear_queue_opt: Should queue be cleared
    :param ephemeral: Should bot response be ephemeral
    :return: ReturnData
    """
    log(ctx, 'loop_command_def', options=locals(), log_type='function', author=ctx.author)

    guild_id, guild_object = ctx.guild.id, ctx.guild
    db_guild = guild(glob, guild_id)

    if not ctx.interaction.response.is_done():
        await ctx.defer(ephemeral=ephemeral)

    # add now_playing to queue if loop is activated
    add_to_queue_when_activated = False

    options = db_guild.options

    if clear_queue_opt:
        if options.loop:
            message = txt(guild_id, glob, "Loop mode is already enabled") + f" {glob.notif}"
            await ctx.reply(message, ephemeral=ephemeral)
            return ReturnData(False, message)

        if not db_guild.now_playing or not guild_object.voice_client.is_playing:
            message = txt(guild_id, glob, "There is no song playing right **now**") + f" {glob.notif}"
            await ctx.reply(message, ephemeral=ephemeral)
            return ReturnData(False, message)

        clear_queue(glob, guild_id)
        await to_queue(glob, guild_id, db_guild.now_playing)
        db_guild.options.loop = True
        update(glob)

        message = f'{txt(guild_id, glob, "Queue **cleared**, Player will now loop **currently** playing song:")} [`{db_guild.now_playing.title}`](<{db_guild.now_playing.url}>) {glob.notif}'
        await ctx.reply(message)
        return ReturnData(True, message)

    if options.loop:
        db_guild.options.loop = False
        update(glob)

        message = txt(guild_id, glob, "Loop mode: `False`") + f" {glob.notif}"
        await ctx.reply(message, ephemeral=ephemeral)
        return ReturnData(True, message)

    db_guild.options.loop = True
    if db_guild.now_playing and add_to_queue_when_activated:
        await to_queue(glob, guild_id, db_guild.now_playing)
    update(glob)

    message = txt(guild_id, glob, 'Loop mode: `True`') + f" {glob.notif}"
    await ctx.reply(message, ephemeral=True)
    return ReturnData(True, message)

async def set_video_time(ctx, glob: GlobalVars, time_stamp: int, mute_response: bool=False, ephemeral: bool=False):
    log(ctx, 'set_video_time', options=locals(), log_type='function')
    ctx_guild_id, ctx_guild_object = ctx.guild.id, ctx.guild

    if not ctx.interaction.response.is_done():
        await ctx.defer(ephemeral=ephemeral)

    try:
        time_stamp = int(time_stamp)
    except (ValueError, TypeError):
        try:
            time_stamp = int(float(time_stamp))
        except (ValueError, TypeError):
            message = f'({time_stamp}) ' + txt(ctx_guild_id, glob, 'is not an int') + f" {glob.notif}"
            if not mute_response:
                await ctx.reply(message, ephemeral=ephemeral)
            return ReturnData(False, message)

    voice = ctx_guild_object.voice_client
    if not voice:
        message = txt(ctx_guild_id, glob, f'Bot is not in a voice channel') + f" {glob.notif}"
        if not mute_response:
            await ctx.reply(message, ephemeral=ephemeral)
        return ReturnData(False, message)

    # if not voice.is_playing():
    #     message = f'Bot is not playing anything'
    #     if not mute_response:
    #         await ctx.reply(message, ephemeral=ephemeral)
    #     return ReturnData(False, message)

    now_playing_video = guild(glob, ctx_guild_id).now_playing
    if not now_playing_video:
        message = txt(ctx_guild_id, glob, f'Bot is not playing anything') + f" {glob.notif}"
        if not mute_response:
            await ctx.reply(message, ephemeral=ephemeral)
        return ReturnData(False, message)

    url = now_playing_video.stream_url
    if not url:
        url = now_playing_video.url

    new_source, new_additional_data = await GetSource.create_source(glob, ctx_guild_id, url, time_stamp=time_stamp, video_class=now_playing_video, source_type=now_playing_video.class_type)

    voice.source = new_source
    set_new_time(glob, now_playing_video, time_stamp)

    message = txt(ctx_guild_id, glob, f'Video time set to') + ": " + str(time_stamp) + f" {glob.notif}"
    if not mute_response:
        await ctx.reply(message, ephemeral=ephemeral)
    return ReturnData(True, message)
