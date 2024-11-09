from classes.data_classes import ReturnData

from database.guild import guild, clear_queue

from utils.log import log
from utils.translate import txt
from utils.save import update
from utils.discord import get_voice_client
from utils.video_time import set_stopped, set_resumed
from utils.global_vars import GlobalVars

from discord.ext import commands as dc_commands
from typing import Union
import discord
import traceback


async def stop_def(ctx, glob: GlobalVars, mute_response: bool = False, keep_loop: bool = False) -> ReturnData:
    """
    Stops player
    :param ctx: Context
    :param glob: GlobalVars
    :param mute_response: Should bot response be muted
    :param keep_loop: Should loop be kept
    :return: ReturnData
    """
    log(ctx, 'stop_def', options=locals(), log_type='function', author=ctx.author)
    guild_id = ctx.guild.id
    db_guild = guild(glob, guild_id)

    voice: discord.voice_client.VoiceClient = get_voice_client(glob.bot.voice_clients, guild=ctx.guild)

    if not voice:
        message = txt(guild_id, glob, "Bot is not connected to a voice channel") + f' {glob.notif}'
        if not mute_response:
            await ctx.reply(message, ephemeral=True)
        return ReturnData(False, message)

    voice.stop()

    with glob.ses.no_autoflush:
        db_guild.options.stopped = True
        if not keep_loop:
            db_guild.options.loop = False
        glob.ses.commit()

    message = txt(guild_id, glob, "Player **stopped!**") + f' {glob.notif}'
    if not mute_response:
        await ctx.reply(message, ephemeral=True)
    return ReturnData(True, message)

async def pause_def(ctx, glob, mute_response: bool = False) -> ReturnData:
    """
    Pause player
    :param ctx: Context
    :param glob: GlobalVars
    :param mute_response: Should bot response be muted
    :return: ReturnData
    """
    log(ctx, 'pause_def', options=locals(), log_type='function', author=ctx.author)
    guild_id = ctx.guild.id
    db_guild = guild(glob, guild_id)

    voice: discord.voice_client.VoiceClient = get_voice_client(glob.bot.voice_clients, guild=ctx.guild)

    if voice:
        if voice.is_playing():
            voice.pause()
            if db_guild.now_playing:
                set_stopped(glob, db_guild.now_playing)
            message = txt(guild_id, glob, "Player **paused!**") + f' {glob.notif}'
            resp = True
        elif voice.is_paused():
            message = txt(guild_id, glob, "Player **already paused!**") + f' {glob.notif}'
            resp = False
        else:
            message = txt(guild_id, glob, 'No audio playing') + f' {glob.notif}'
            resp = False
    else:
        message = txt(guild_id, glob, "Bot is not connected to a voice channel") + f' {glob.notif}'
        resp = False

    update(glob)

    if not mute_response:
        await ctx.reply(message, ephemeral=True)
    return ReturnData(resp, message)

async def resume_def(ctx, glob: GlobalVars, mute_response: bool = False) -> ReturnData:
    """
    Resume player
    :param ctx: Context
    :param glob: GlobalVars
    :param mute_response: Should bot response be muted
    :return: ReturnData
    """
    log(ctx, 'resume_def', options=locals(), log_type='function', author=ctx.author)
    guild_id = ctx.guild.id
    db_guild = guild(glob, guild_id)

    voice: discord.voice_client.VoiceClient = get_voice_client(glob.bot.voice_clients, guild=ctx.guild)

    if voice:
        if voice.is_paused():
            voice.resume()
            if db_guild.now_playing:
                set_resumed(glob, db_guild.now_playing)
            message = txt(guild_id, glob, "Player **resumed!**") + f' {glob.notif}'
            resp = True
        elif voice.is_playing():
            message = txt(guild_id, glob, "Player **already resumed!**") + f' {glob.notif}'
            resp = False
        else:
            message = txt(guild_id, glob, 'No audio playing') + f' {glob.notif}'
            resp = False
    else:
        message = txt(guild_id, glob, "Bot is not connected to a voice channel") + f' {glob.notif}'
        resp = False

    update(glob)

    if not mute_response:
        await ctx.reply(message, ephemeral=True)
    return ReturnData(resp, message)

async def join_def(ctx, glob: GlobalVars, channel_id=None, mute_response: bool = False) -> ReturnData:
    """
    Join voice channel
    :param ctx: Context
    :param glob: GlobalVars
    :param channel_id: id of channel to join
    :param mute_response: Should bot response be muted
    :return: ReturnData
    """
    log(ctx, 'join_def', options=locals(), log_type='function', author=ctx.author)
    guild_id, guild_object = ctx.guild.id, ctx.guild

    # define author channel (for ide)
    author_channel = None

    if not channel_id:
        if not ctx.author.voice:
            message = txt(guild_id, glob, "You are **not connected** to a voice channel") + f' {glob.notif}'
            await ctx.reply(message, ephemeral=True)
            return ReturnData(False, message)

        author_channel = ctx.author.voice.channel

        if ctx.voice_client:
            if ctx.voice_client.channel == author_channel:
                message = txt(guild_id, glob, "I'm already in this channel") + f' {glob.notif}'
                if not mute_response:
                    await ctx.reply(message, ephemeral=True)
                return ReturnData(True, message)

    try:
        voice_channel = author_channel if author_channel else glob.bot.get_channel(int(channel_id))

        # check if bot has permission to join channel
        if not voice_channel.permissions_for(guild_object.me).connect:
            message = txt(guild_id, glob, "I don't have permission to join this channel") + f' {glob.notif}'
            await ctx.reply(message, ephemeral=True)
            return ReturnData(False, message)

        # check if bot has permission to speak in channel
        if not voice_channel.permissions_for(guild_object.me).speak:
            message = txt(guild_id, glob, "I don't have permission to speak in this channel") + f' {glob.notif}'
            await ctx.reply(message, ephemeral=True)
            return ReturnData(False, message)

        # check if the channel is empty
        if not len(voice_channel.members) > 0:
            message = txt(guild_id, glob, "The channel is empty") + f' {glob.notif}'
            await ctx.reply(message, ephemeral=True)
            return ReturnData(False, message)

        if guild_object.voice_client:
            await guild_object.voice_client.disconnect(force=True)

        await voice_channel.connect()
        await guild_object.change_voice_state(channel=voice_channel, self_deaf=True)

        message = f"{txt(guild_id, glob, 'Joined voice channel:')}  `{voice_channel.name}`" + f' {glob.notif}'
        if not mute_response:
            await ctx.reply(message, ephemeral=True)
        return ReturnData(True, message)

    except (discord.ext.commands.errors.CommandInvokeError, discord.errors.ClientException, AttributeError, ValueError,
            TypeError):
        log(ctx, "------------------------------- join -------------------------")
        tb = traceback.format_exc()
        log(ctx, tb)
        log(ctx, "--------------------------------------------------------------")

        message = txt(guild_id, glob, "Channel **doesn't exist** or bot doesn't have **sufficient permission** to join") + f' {glob.notif}'
        await ctx.reply(message, ephemeral=True)
        return ReturnData(False, message)

async def disconnect_def(ctx, glob: GlobalVars, mute_response: bool = False) -> ReturnData:
    """
    Disconnect bot from voice channel
    :param ctx: Context
    :param glob: GlobalVars
    :param mute_response: Should bot response be muted
    :return: ReturnData
    """
    log(ctx, 'disconnect_def', options=locals(), log_type='function', author=ctx.author)
    guild_id, guild_object = ctx.guild.id, ctx.guild

    if guild_object.voice_client:
        await stop_def(ctx, glob, mute_response=True)
        clear_queue(glob, guild_id)

        channel = guild_object.voice_client.channel
        await guild_object.voice_client.disconnect(force=True)

        message = f"{txt(guild_id, glob, 'Left voice channel:')} `{channel}`" + f' {glob.notif}'
        if not mute_response:
            await ctx.reply(message, ephemeral=True)
        return ReturnData(True, message)
    else:
        message = txt(guild_id, glob, "Bot is **not** in a voice channel") + f' {glob.notif}'
        if not mute_response:
            await ctx.reply(message, ephemeral=True)
        return ReturnData(False, message)

async def volume_command_def(ctx, glob: GlobalVars, volume: Union[float, int] = None, ephemeral: bool = False, mute_response: bool = False) -> ReturnData:
    """
    Change volume of player
    :param ctx: Context
    :param glob: GlobalVars
    :param volume: volume to set
    :param ephemeral: Should bot response be ephemeral
    :param mute_response: Should bot response be muted
    :return: ReturnData
    """
    log(ctx, 'volume_command_def', options=locals(), log_type='function', author=ctx.author)
    guild_id, guild_object = ctx.guild.id, ctx.guild
    db_guild = guild(glob, guild_id)

    if volume:
        try:
            volume = int(volume)
        except (ValueError, TypeError):
            message = txt(guild_id, glob, f'Invalid volume') + f' {glob.notif}'
            if not mute_response:
                await ctx.reply(message, ephemeral=ephemeral)
            return ReturnData(False, message)

        new_volume = volume / 100

        db_guild.options.volume = new_volume
        glob.ses.commit()
        voice = guild_object.voice_client
        if voice:
            try:
                if voice.source:
                    voice.source.volume = new_volume
                    # voice.source = discord.PCMVolumeTransformer(voice.source, volume=new_volume) -- just trouble
            except AttributeError:
                pass

        message = f'{txt(guild_id, glob, "Changed the volume for this server to:")} `{int(db_guild.options.volume * 100)}%`' + f' {glob.notif}'
    else:
        message = f'{txt(guild_id, glob, "The volume for this server is:")} `{int(db_guild.options.volume * 100)}%`' + f' {glob.notif}'

    update(glob)

    if not mute_response:
        await ctx.reply(message, ephemeral=ephemeral)
    return ReturnData(True, message)
