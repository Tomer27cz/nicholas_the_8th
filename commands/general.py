from classes.data_classes import ReturnData

from database.guild import guild

from utils.log import log
from utils.translate import txt
from utils.save import update
from utils.global_vars import languages_dict, GlobalVars
from utils.convert import convert_duration
from utils.discord import create_embed

import commands.admin

from typing import Literal
import discord

async def ping_def(ctx, glob: GlobalVars) -> ReturnData:
    """
    Ping command
    :param ctx: Context
    :param glob: GlobalVars
    :return: ReturnData
    """
    log(ctx, 'ping_def', options=locals(), log_type='function', author=ctx.author)
    update(glob)

    message = f'**Pong!** Latency: {round(glob.bot.latency * 1000)}ms {glob.notif}'
    await ctx.reply(message)
    return ReturnData(True, message)

# noinspection PyTypeHints
async def language_command_def(ctx, glob: GlobalVars, country_code: Literal[tuple(languages_dict)]) -> ReturnData:
    """
    Change language of bot in guild
    :param ctx: Context
    :param glob: GlobalVars
    :param country_code: Country code of language (e.g. en, cs, sk ...)
    :return: ReturnData
    """
    log(ctx, 'language_command_def', options=locals(), log_type='function', author=ctx.author)
    db_guild = guild(glob, ctx.guild.id)

    db_guild.options.language = country_code
    update(glob)

    message = f'{txt(ctx.guild.id, glob, "Changed the language for this server to: ")} `{db_guild.options.language}` {glob.notif}'
    await ctx.reply(message)
    return ReturnData(True, message)

async def list_command_def(ctx, glob: GlobalVars, display_type: Literal['short', 'medium', 'long']=None, ephemeral: bool = True) -> ReturnData:
    """
    List the queue
    :param ctx: Context
    :param glob: GlobalVars
    :param display_type: Type of list (short, medium, long) - text, embed, embed with info and picture
    :param ephemeral: Should bot response be ephemeral
    :return: ReturnData
    """
    log(ctx, 'list_def', options=locals(), log_type='function', author=ctx.author)
    guild_id = ctx.guild.id

    db_guild = guild(glob, guild_id)
    max_embed = 5

    if not db_guild.queue:
        message = txt(guild_id, glob, "Nothing to **show**, queue is **empty!**") + f" {glob.notif}"
        await ctx.reply(message, ephemeral=ephemeral)
        return ReturnData(True, message)

    display_type = display_type if display_type else 'long' if len(db_guild.queue) <= max_embed else 'short'
    loop = db_guild.options.loop
    key = db_guild.data.key

    if display_type == 'long':
        message = f"**THE QUEUE**\n **Loop** mode  `{loop}`,  **Display** type `{display_type}` {glob.notif}"
        await ctx.send(message, ephemeral=ephemeral, mention_author=False)

        for index, val in enumerate(db_guild.queue):
            embed = create_embed(glob, val, f'{txt(guild_id, glob, f"QUEUE #")}{index}', guild_id)
            await ctx.send(embed=embed, ephemeral=ephemeral, mention_author=False, silent=True)

        return ReturnData(True, f'Queue list')

    if display_type == 'medium':
        embed = discord.Embed(title=f"Song Queue", color=0x00ff00, description=f'Loop: {loop} | Display type: {display_type} {glob.notif}')

        message = ''
        for index, val in enumerate(db_guild.queue):
            add = f'**{index}** --> `{convert_duration(val.duration)}`  [{val.title}](<{val.url}>) \n'

            if len(message) + len(add) > 1023:
                embed.add_field(name="", value=message, inline=False)
                message = ''
                continue

            message = message + add

        embed.add_field(name="", value=message, inline=False)

        if len(embed) < 6000:
            await ctx.reply(embed=embed, ephemeral=ephemeral, mention_author=False)
            return ReturnData(True, f'Queue list')

        await ctx.reply("HTTPException(discord 6000 character limit) >> using display type `short`", ephemeral=ephemeral, mention_author=False)
        display_type = 'short'

    if display_type == 'short':
        send = f"**THE QUEUE**\n **Loop** mode  `{loop}`,  **Display** type `{display_type}` {glob.notif}"
        # noinspection PyUnresolvedReferences
        if ctx.interaction.response.is_done():
            await ctx.send(send, ephemeral=ephemeral, mention_author=False)
        else:
            await ctx.reply(send, ephemeral=ephemeral, mention_author=False)

        message = ''
        for index, val in enumerate(db_guild.queue):
            add = f'**{txt(guild_id, glob, f"QUEUE #")}{index}**  `{convert_duration(val.duration)}`  [`{val.title}`](<{val.url}>) \n'

            if len(message) + len(add) > 2000:
                if ephemeral:
                    await ctx.send(message, ephemeral=ephemeral, mention_author=False)
                    message = ''
                    continue

                await ctx.message.channel.send(content=message, mention_author=False)
                message = ''
                continue

            message = message + add

        update(glob)

        if ephemeral:
            await ctx.send(message, ephemeral=ephemeral, mention_author=False)
            return ReturnData(True, f'Queue list')

        await ctx.message.channel.send(content=message, mention_author=False)
        return ReturnData(True, f'Queue list')

    message = txt(guild_id, glob, 'Wrong list type')
    await ctx.reply(message, ephemeral=ephemeral)
    return ReturnData(False, message)

async def options_command_def(ctx, glob: GlobalVars, loop=None, language=None, response_type=None, buttons=None, volume=None, buffer=None) -> ReturnData:
    log(ctx, 'options_command_def', options=locals(), log_type='function', author=ctx.author)

    if all(v is None for v in [loop, language, response_type, buttons, volume, buffer]):
        return await commands.admin.options_def(ctx, glob, server=None, ephemeral=False)

    return await commands.admin.options_def(ctx, glob, server=ctx.guild.id, ephemeral=False, loop=str(loop), language=str(language), response_type=str(response_type), buttons=str(buttons), volume=str(volume), buffer=str(buffer))