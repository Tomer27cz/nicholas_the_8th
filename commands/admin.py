from classes.data_classes import ReturnData

from database.guild import guild, guild_ids

from utils.log import log
from utils.translate import txt
from utils.save import update
from utils.convert import to_bool
from utils.global_vars import languages_dict, GlobalVars

from discord.ext import commands as dc_commands
from typing import Union

import sys

async def kys_def(ctx: dc_commands.Context, glob: GlobalVars):
    log(ctx, 'kys_def', options=locals(), log_type='function', author=ctx.author)
    guild_id = ctx.guild.id
    await ctx.reply(txt(guild_id, glob, "Committing seppuku..."))
    sys.exit(3)

# noinspection DuplicatedCode
async def options_def(ctx: dc_commands.Context, glob: GlobalVars,
                      server: Union[str, int, None]=None,
                      stopped: str = None,
                      loop: str = None,
                      buttons: str = None,
                      language: str = None,
                      response_type: str = None,
                      buffer: str = None,
                      volume: str = None,
                      ephemeral=True
                      ):
    log(ctx, 'options_def', options=locals(), log_type='function', author=ctx.author)
    guild_id, guild_object = ctx.guild.id, ctx.guild

    guilds_to_change = []
    if server is None:
        pass

    elif server == 'this':
        guilds_to_change.append(guild_id)

    elif server == 'all':
        for _guild_id in guild_ids(glob):
            guilds_to_change.append(_guild_id)

    else:
        try:
            server = int(server)
        except (ValueError, TypeError):
            message = txt(guild_id, glob, "That is not a **guild id!**")
            await ctx.reply(message, ephemeral=ephemeral)
            return ReturnData(False, message)

        if server not in guild_ids(glob):
            message = txt(guild_id, glob, "That guild doesn't exist or the bot is not in it")
            await ctx.reply(message, ephemeral=ephemeral)
            return ReturnData(False, message)

        guilds_to_change.append(server)

    for for_guild_id in guilds_to_change:
        options = guild(glob, for_guild_id).options

        bool_list_t = ['True', 'true', '1']
        bool_list_f = ['False', 'false', '0']
        bool_list = bool_list_f + bool_list_t

        response_types = ['long', 'short']

        def check_none(value):
            if value == 'None':
                return None
            return value

        stopped = check_none(stopped)
        loop = check_none(loop)
        buttons = check_none(buttons)
        language = check_none(language)
        response_type = check_none(response_type)
        buffer = check_none(buffer)
        volume = check_none(volume)

        async def bool_check(value):
            if value is None:
                return ReturnData(True, 'value is None')

            if value not in bool_list:
                _msg = f'{value.__name__} has to be: {bool_list} --> {value}'
                await ctx.reply(_msg, ephemeral=ephemeral)
                return ReturnData(False, _msg)

            return ReturnData(True, 'value is ok')

        stopped_check = await bool_check(stopped)
        if not stopped_check.response:
            return stopped_check

        loop_check = await bool_check(loop)
        if not loop_check.response:
            return loop_check

        buttons_check = await bool_check(buttons)
        if not buttons_check.response:
            return buttons_check

        async def is_resp_type(value):
            if value is None:
                return ReturnData(True, 'value is None')

            if value not in response_types:
                _msg = f'{value.__name__} has to be: {response_types} --> {value}'
                await ctx.reply(_msg, ephemeral=ephemeral)
                return ReturnData(False, _msg)

            return ReturnData(True, 'value is ok')

        response_type_check = await is_resp_type(response_type)
        if not response_type_check.response:
            return response_type_check

        async def is_lang(value):
            if value is None:
                return ReturnData(True, 'value is None')

            if value not in languages_dict.keys():
                _msg = f'{value.__name__} has to be: {languages_dict.keys()} --> {value}'
                await ctx.reply(_msg, ephemeral=ephemeral)
                return ReturnData(False, _msg)

            return ReturnData(True, 'value is ok')

        language_check = await is_lang(language)
        if not language_check.response:
            return language_check

        async def is_int(value):
            if value is None:
                return ReturnData(True, 'value is None')

            if not value.isdigit():
                _msg = f'{value.__name__} has to be a number: {value}'
                await ctx.reply(_msg, ephemeral=ephemeral)
                return ReturnData(False, _msg)

            return ReturnData(True, 'value is ok')

        volume_check = await is_int(volume)
        if not volume_check.response:
            return volume_check

        buffer_check = await is_int(buffer)
        if not buffer_check.response:
            return buffer_check


        options.stopped = to_bool(stopped) if stopped is not None else options.stopped
        options.loop = to_bool(loop) if loop is not None else options.loop
        options.buttons = to_bool(buttons) if buttons is not None else options.buttons

        options.language = language if language is not None else options.language
        options.response_type = response_type if response_type is not None else options.response_type

        options.volume = float(int(volume) / 100) if volume is not None else options.volume
        options.buffer = int(buffer) if buffer is not None else options.buffer

        update(glob)

    if len(guilds_to_change) < 2:
        if len(guilds_to_change) == 0:
            db_guild = guild(glob, guild_id)
            options = db_guild.options
            add = False
        else:
            db_guild = guild(glob, guilds_to_change[0])
            options = db_guild.options
            add = True

        message = f"""
        {txt(guild_id, glob, f'Edited options successfully!') + f' - `{db_guild.id}` ({db_guild.data.name})' if add else ''}\n**Options:**
        stopped -> `{options.stopped}`
        loop -> `{options.loop}`
        buttons -> `{options.buttons}`
        language -> `{options.language}`
        response_type -> `{options.response_type}`
        buffer -> `{options.buffer}`
        volume -> `{options.volume*100}`
        """

        await ctx.reply(message, ephemeral=ephemeral)
        return ReturnData(True, message)

    message = txt(guild_id, glob, f'Edited options successfully!')
    await ctx.reply(message, ephemeral=ephemeral)
    return ReturnData(True, message)
