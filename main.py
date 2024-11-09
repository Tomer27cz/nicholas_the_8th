from classes.data_classes import Guild
from classes.typed_dictionaries import LastUpdated

from commands.autocomplete import *

from utils.discord import get_content_of_message
from utils.log import send_to_admin
from utils.save import update_db_commands

from commands.admin import *
from commands.general import *
from commands.player import *
from commands.queue import *
from commands.radio import *
from commands.voice import *

from sclib import SoundcloudAPI
from spotipy.oauth2 import SpotifyClientCredentials
from discord.ext import commands as dc_commands
from discord import app_commands
import discord.ext.commands
import spotipy

import config

authorized_users = config.AUTHORIZED_USERS
my_id = config.OWNER_ID
bot_id = config.CLIENT_ID
prefix = config.PREFIX
vlc_logo = config.VLC_LOGO
default_discord_avatar = config.DEFAULT_DISCORD_AVATAR
d_id = 349164237605568513
notif = config.NOTIF

# ---------------- Connect to database ------------

from database.main import *
from database.guild import *

ses = connect_to_db(first_time=True)

# ---------------- Bot class ------------

class Bot(dc_commands.Bot):
    """
    Bot class

    This class is used to create the bot instance.
    """
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(command_prefix=prefix, intents=intents)
        self.synced = False

    async def on_ready(self):
        await self.wait_until_ready()
        if not self.synced:
            log(None, "Trying to sync commands")
            await self.tree.sync()
            log(None, f"Synced slash commands for {self.user}")
            update_db_commands(glob)
            log(None, "Updated database commands")
        await bot.change_presence(activity=discord.Game(name=f"/help"))
        log(None, f'Logged in as:\n{bot.user.name}\n{bot.user.id}')

        update(glob)

    async def on_guild_join(self, guild_object):
        # log
        log_msg = f"Joined guild ({guild_object.name})({guild_object.id}) with {guild_object.member_count} members and {len(guild_object.voice_channels)} voice channels"
        log(None, log_msg)

        # send log to admin
        await send_to_admin(glob, log_msg)

        # create guild object
        create_guild(glob, guild_object.id)
        update(glob)

        # get text channels
        text_channels = guild_object.text_channels
        sys_channel = guild_object.system_channel

        # send welcome message in system channel or first text channel
        message = f"Hello **`{guild_object.name}`**! I am `{self.user.display_name}`. Thank you for inviting me.\n\nTo see what commands I have available type `/help`\n\nIf you have any questions, you can DM my developer <@!{config.DEVELOPER_ID}>#4272"
        if sys_channel is not None:
            if sys_channel.permissions_for(guild_object.me).send_messages:
                await sys_channel.send(message)
        else:
            await text_channels[0].send(message)

    @staticmethod
    async def on_guild_remove(guild_object):
        # log
        log_msg = f"Left guild ({guild_object.name})({guild_object.id}) with {guild_object.member_count} members and {len(guild_object.voice_channels)} voice channels"
        log(None, log_msg)

        # send log to admin
        await send_to_admin(glob, log_msg)

        # update guilds
        update(glob)

    async def on_voice_state_update(self, member, before, after):
        try:
            voice_state = member.guild.voice_client
            guild_id = member.guild.id

            # check if bot is alone in voice channel
            if voice_state is not None and len(voice_state.channel.members) == 1:
                voice_state.stop()
                await voice_state.disconnect()

                guild(glob, guild_id).options.stopped = True
                ses.commit()

                clear_queue(glob, guild_id)

                log(guild_id, "-->> Disconnected when last person left -> Queue Cleared <<--")

            # checks if member is bot, if not do not count the buffer
            if not member.id == self.user.id:
                return

            # if bot joins a voice channel, start buffer
            if before.channel is None:
                voice = after.channel.guild.voice_client

                time_var = 0
                while True:
                    await asyncio.sleep(10)
                    time_var += 10

                    if voice.is_playing():
                        time_var = 0
                        continue

                    # if voice.is_paused():
                    #     time_var = 0
                    #     continue

                    if time_var >= guild(glob, guild_id).options.buffer:
                        voice.stop()
                        await voice.disconnect()

                        guild(glob, guild_id).options.stopped = True
                        ses.commit()

                        log(guild_id, f"-->> Disconnecting after {guild(glob, guild_id).options.buffer} seconds of no play <<--")

                    # At the end if disconnect caused by buffer
                    if not voice.is_connected():
                        break

            # if bot leaves a voice channel
            elif after.channel is None:
                guild(glob, guild_id).options.stopped = True
                ses.commit()
                clear_queue(glob, guild_id)
                log(guild_id, f"-->> Cleared Queue after bot Disconnected <<--")
        except Exception as error:
            await self.error_handler(None, error)

    async def on_command_error(self, ctx, error):
        await self.error_handler(ctx, error)

    async def on_message(self, message):
        try:
            # on every message
            if message.author == bot.user:
                return

            # check if message is a DM
            if not message.guild:
                # send DM to ADMIN
                await send_to_admin(glob, f"<@!{message.author.id}> tied to DM me with this message `{message.content}`")
                try:
                    # respond to DM
                    await message.channel.send(
                        f"I'm sorry, but I only work in servers.\n\n"
                        f""
                        f"If you want me to join your server, you can invite me with this link: {config.INVITE_URL}\n\n"
                        f""
                        f"If you have any questions, you can DM my developer <@!{config.DEVELOPER_ID}>#4272")
                    return

                except discord.errors.Forbidden:
                    return

            await bot.process_commands(message)
        except Exception as error:
            await self.error_handler(None, error)

    async def error_handler(self, ctx, error):
        # get error traceback
        error_traceback = traceback.format_exception(type(error), error, error.__traceback__)
        error_traceback = ''.join(error_traceback)

        err_msg = f"Error: ({error})\nType: ({type(error)})\nAuthor: ({getattr(ctx, 'author', None)})\nCommand: ({getattr(ctx, 'command', None)})\nKwargs: ({getattr(ctx, 'kwargs', None)})"

        if isinstance(error, discord.errors.Forbidden):
            log(ctx, 'error.Forbidden', {'error': error}, log_type='error', author=getattr(ctx, 'author', None))
            await send_to_admin(glob, err_msg, file=True)
            if ctx:
                await ctx.send(txt(ctx.guild.id, glob,"The command failed because I don't have the required permissions.\n Please give me the required permissions and try again."))
            return

        if isinstance(error, dc_commands.CheckFailure):
            log(ctx, err_msg, log_type='error', author=getattr(ctx, 'author', None))
            await send_to_admin(glob, err_msg, file=True)
            if ctx:
                await ctx.reply(f"（ ͡° ͜ʖ ͡°)つ━☆・。\n"
                                f"⊂　　 ノ 　　　・゜+.\n"
                                f"　しーＪ　　　°。+ ´¨)\n"
                                f"　　　　　　　　　.· ´¸.·´¨) ¸.·*¨)\n"
                                f"　　　　　　　　　　(¸.·´ (¸.·' ☆ **Fuck off**\n"
                                f"*{txt(ctx.guild.id, glob, 'You dont have permission to use this command')}*")
            return

        if isinstance(error, dc_commands.MissingPermissions):
            log(ctx, err_msg, log_type='error', author=getattr(ctx, 'author', None))
            await send_to_admin(glob, err_msg, file=True)
            if ctx:
                await ctx.reply(txt(ctx.guild.id, glob,'Bot does not have permissions to execute this command correctly') + f" - {error}")
            return

        if 'Video unavailable.' in str(error):
            try:
                error = error.original.original
            except AttributeError:
                pass

            if ctx:
                await ctx.reply(f'{error} -> It *may be* ***GeoBlocked*** in `Czechia` (bot server location)')
            return

        try:
            # error.__cause__.__cause__ = HybridCommandError -> CommandInvokeError -> {Exception}
            if isinstance(error.__cause__.__cause__, PendingRollbackError):
                log(ctx, err_msg, log_type='error', author=getattr(ctx, 'author', None))

                try:
                    await send_to_admin(glob, "Attempting Rollback" + err_msg, file=True)
                    glob.ses.rollback()  # Rollback the session
                    await send_to_admin(glob, "Rollback Successful", file=False)
                    err_msg += "\nRollback Successful"
                except Exception as rollback_error:
                    rollback_traceback = traceback.format_exception(type(rollback_error), rollback_error,
                                                                    rollback_error.__traceback__)
                    rollback_traceback = ''.join(rollback_traceback)

                    err_msg += f"\nFailed Rollback: ({rollback_error})\nRollback Traceback: \n{rollback_traceback}"
                    log(ctx, err_msg, log_type='error', author=getattr(ctx, 'author', None))

                err_msg += f"\n{'-' * 50}\nOriginal Traceback: \n{error_traceback}"
                await send_to_admin(glob, err_msg, file=True)

                if ctx:
                    await ctx.reply(f"Database error -> Attempted rollback (try again one time - if it doesn't work tell developer to restart bot)")
        except AttributeError as _e:
            # message = f"Error for ({getattr(ctx, 'author', None)}) -> ({ctx.command}) with error ({error})\n{error_traceback}\n\n{_e}"
            pass

        err_msg += f"\nTraceback: \n{error_traceback}"
        log(ctx, err_msg, log_type='error', author=getattr(ctx, 'author', None))

        await send_to_admin(glob, err_msg, file=True)
        if ctx:
            await ctx.reply(f"{error}   {bot.get_user(config.DEVELOPER_ID).mention}", ephemeral=True)

# ---------------------------------------------- LOAD ------------------------------------------------------------------

log(None, "--------------------------------------- NEW / REBOOTED ----------------------------------------")

log(None, 'Loaded radio.json')

authorized_users += [my_id, d_id, config.DEVELOPER_ID, 349164237605568513]
log(None, 'Loaded languages.json')

# ---------------------------------------------- BOT -------------------------------------------------------------------

bot = Bot()

log(None, 'Discord API initialized')

# ---------------------------------------------- SPOTIPY ---------------------------------------------------------------

try:
    credentials = SpotifyClientCredentials(client_id=config.SPOTIFY_CLIENT_ID,
                                           client_secret=config.SPOTIFY_CLIENT_SECRET)
    spotify_api = spotipy.Spotify(client_credentials_manager=credentials)
    log(None, 'Spotify API initialized')
except spotipy.oauth2.SpotifyOauthError:
    spotify_api = None
    log(None, 'Failed to initialize Spotify API')

# --------------------------------------------- SOUNDCLOUD -------------------------------------------------------------

try:
    soundcloud_api = SoundcloudAPI(client_id=config.SOUNDCLOUD_CLIENT_ID)
    log(None, 'SoundCloud API initialized')
except Exception as e:
    log(None, f'Failed to initialize SoundCloud API : {e}')
    soundcloud_api = None

# --------------------------------------------- Global Variables --------------------------------------------------------

glob = GlobalVars(bot, ses, spotify_api, soundcloud_api, notif)

# ---------------- set last_updated and keep_alive ------------


# idk about thius maby not needed
async def fix_guilds():
    for guild_obj in glob.ses.query(Guild).all():
        guild_obj.last_updated = {key: int(time()) for key in LastUpdated.__annotations__.keys()}
        guild_obj.keep_alive = True
    glob.ses.commit()

    log(None, 'Set attributes for new start')

# --------------------------------------- QUEUE --------------------------------------------------

@bot.hybrid_command(name='queue', with_app_command=True, description=txt(0, glob, 'command_queue'), help=txt(0, glob, 'command_queue'), extras={'category': 'queue'})
@app_commands.describe(query=txt(0, glob, 'query'), position=txt(0, glob, 'attr_queue_position'))
async def queue_command(ctx: dc_commands.Context, query, position: int = None):
    log(ctx, 'queue', options=locals(), log_type='command', author=ctx.author)
    await queue_command_def(ctx, glob, query, position=position)

@bot.hybrid_command(name='skip', with_app_command=True, description=txt(0, glob, 'command_skip'), help=txt(0, glob, 'command_skip'), extras={'category': 'queue'})
async def skip(ctx: dc_commands.Context):
    log(ctx, 'skip', options=locals(), log_type='command', author=ctx.author)
    await skip_def(ctx, glob)

@bot.hybrid_command(name='remove', with_app_command=True, description=txt(0, glob, 'command_remove'),
                    help=txt(0, glob, 'command_remove'), extras={'category': 'queue'})
@app_commands.describe(song=txt(0, glob, 'attr_remove_song'), user_only=txt(0, glob, 'ephemeral'))
async def remove(ctx: dc_commands.Context, song, user_only: bool = False):
    log(ctx, 'remove', options=locals(), log_type='command', author=ctx.author)
    await remove_def(ctx, glob, song, ephemeral=user_only)

@bot.hybrid_command(name='clear', with_app_command=True, description=txt(0, glob, 'command_clear'),
                    help=txt(0, glob, 'command_clear'), extras={'category': 'queue'})
@app_commands.describe(user_only=txt(0, glob, 'ephemeral'))
async def clear(ctx: dc_commands.Context, user_only: bool = False):
    log(ctx, 'clear', options=locals(), log_type='command', author=ctx.author)
    await clear_def(ctx, glob, user_only)

@bot.hybrid_command(name='shuffle', with_app_command=True, description=txt(0, glob, 'command_shuffle'),
                    help=txt(0, glob, 'command_shuffle'), extras={'category': 'queue'})
@app_commands.describe(user_only=txt(0, glob, 'ephemeral'))
async def shuffle(ctx: dc_commands.Context, user_only: bool = False):
    log(ctx, 'shuffle', options=locals(), log_type='command', author=ctx.author)
    await shuffle_def(ctx, glob, user_only)

@bot.hybrid_command(name='search', with_app_command=True, description=txt(0, glob, 'command_search'),
                    help=txt(0, glob, 'command_search'), extras={'category': 'queue'})
@app_commands.describe(query=txt(0, glob, 'query'), display_type=txt(0, glob, 'attr_search_display_type'),
                       force=txt(0, glob, 'attr_search_force'), user_only=txt(0, glob, 'ephemeral'))
async def search_command(ctx: dc_commands.Context, query, display_type: Literal['short', 'long'] = None,
                         force: bool = False, user_only: bool = False):
    log(ctx, 'search', options=locals(), log_type='command', author=ctx.author)
    await search_command_def(ctx, glob, query, display_type, force, user_only)

# --------------------------------------- PLAYER --------------------------------------------------

@bot.hybrid_command(name='play', with_app_command=True, description=txt(0, glob, 'command_play'), help=txt(0, glob, 'command_play'), extras={'category': 'player'})
@app_commands.describe(query=txt(0, glob, 'query'), force=txt(0, glob, 'attr_play_force'))
async def play(ctx: dc_commands.Context, query=None, force=False):
    log(ctx, 'play', options=locals(), log_type='command', author=ctx.author)
    await play_def(ctx, glob, query, force)

@bot.hybrid_command(name='nowplaying', with_app_command=True, description=txt(0, glob, 'command_nowplaying'),
                    help=txt(0, glob, 'command_nowplaying'), extras={'category': 'player'})
@app_commands.describe(user_only=txt(0, glob, 'ephemeral'))
async def nowplaying(ctx: dc_commands.Context, user_only: bool = False):
    log(ctx, 'nowplaying', options=locals(), log_type='command', author=ctx.author)
    await now_def(ctx, glob, user_only)

@bot.hybrid_command(name='loop', with_app_command=True, description=txt(0, glob, 'command_loop'), help=txt(0, glob, 'command_loop'), extras={'category': 'player'})
async def loop_command(ctx: dc_commands.Context):
    log(ctx, 'loop', options=locals(), log_type='command', author=ctx.author)
    await loop_command_def(ctx, glob)

@bot.hybrid_command(name='loop-this', with_app_command=True, description=txt(0, glob, 'command_loop_this'),
                    help=txt(0, glob, 'command_loop_this'), extras={'category': 'player'})
async def loop_this(ctx: dc_commands.Context):
    log(ctx, 'loop_this', options=locals(), log_type='command', author=ctx.author)
    await loop_command_def(ctx, glob, clear_queue_opt=True)

# --------------------------------------- RADIO --------------------------------------------------

@bot.hybrid_command(name='radio-cz', with_app_command=True, description=txt(0, glob, 'command_radio_cz'), help=txt(0, glob, 'command_radio_cz'), extras={'category': 'radio'})
@app_commands.describe(radio=txt(0, glob, 'attr_radio_cz_radio'))
async def radio_cz_command(ctx: dc_commands.Context, radio: str):
    log(ctx, 'radio_cz', options=locals(), log_type='command', author=ctx.author)
    await radio_cz_def(ctx, glob, radio)

@bot.hybrid_command(name='radio-garden', with_app_command=True, description=txt(0, glob, 'command_radio_garden'), help=txt(0, glob, 'command_radio_garden'), extras={'category': 'radio'})
@app_commands.describe(radio=txt(0, glob, 'attr_radio_garden_radio'))
async def radio_garden_command(ctx: dc_commands.Context, radio: str):
    log(ctx, 'radio_garden', options=locals(), log_type='command', author=ctx.author)
    await radio_garden_def(ctx, glob, radio)

@bot.hybrid_command(name='radio-tunein', with_app_command=True, description=txt(0, glob, 'command_radio_tunein'), help=txt(0, glob, 'command_radio_tunein'), extras={'category': 'radio'})
@app_commands.describe(radio=txt(0, glob, 'attr_radio_tunein_radio'))
async def radio_tunein_command(ctx: dc_commands.Context, radio: str):
    log(ctx, 'radio_tunein', options=locals(), log_type='command', author=ctx.author)
    await radio_tunein_def(ctx, glob, radio)

# --------------------------------------- VOICE --------------------------------------------------

@bot.hybrid_command(name='stop', with_app_command=True, description=txt(0, glob, 'command_stop'), help=txt(0, glob, 'command_stop'), extras={'category': 'voice'})
async def stop(ctx: dc_commands.Context):
    log(ctx, 'stop', options=locals(), log_type='command', author=ctx.author)
    await stop_def(ctx, glob)

@bot.hybrid_command(name='pause', with_app_command=True, description=txt(0, glob, 'command_pause'), help=txt(0, glob, 'command_pause'), extras={'category': 'voice'})
async def pause(ctx: dc_commands.Context):
    log(ctx, 'pause', options=locals(), log_type='command', author=ctx.author)
    await pause_def(ctx, glob)

@bot.hybrid_command(name='resume', with_app_command=True, description=txt(0, glob, 'command_resume'), help=txt(0, glob, 'command_resume'), extras={'category': 'voice'})
async def resume(ctx: dc_commands.Context):
    log(ctx, 'resume', options=locals(), log_type='command', author=ctx.author)
    await resume_def(ctx, glob)

@bot.hybrid_command(name='join', with_app_command=True, description=txt(0, glob, 'command_join'), help=txt(0, glob, 'command_join'), extras={'category': 'voice'})
@app_commands.describe(channel=txt(0, glob, 'attr_join_channel'))
async def join(ctx: dc_commands.Context, channel: discord.VoiceChannel = None):
    log(ctx, 'join', options=locals(), log_type='command', author=ctx.author)
    await join_def(ctx, glob, channel_id=channel.id if channel else None)

@bot.hybrid_command(name='disconnect', with_app_command=True, description=txt(0, glob, 'command_disconnect'),
                    help=txt(0, glob, 'command_disconnect'), extras={'category': 'voice'})
async def disconnect(ctx: dc_commands.Context):
    log(ctx, 'disconnect', options=locals(), log_type='command', author=ctx.author)
    await disconnect_def(ctx, glob)

@bot.hybrid_command(name='volume', with_app_command=True, description=txt(0, glob, 'command_volume'),
                    help=txt(0, glob, 'command_volume'), extras={'category': 'voice'})
@app_commands.describe(volume=txt(0, glob, 'attr_volume_volume'), user_only=txt(0, glob, 'ephemeral'))
async def volume_command(ctx: dc_commands.Context, volume: int = None, user_only: bool = False):
    log(ctx, 'volume', options=locals(), log_type='command', author=ctx.author)
    await volume_command_def(ctx, glob, volume, user_only)

# --------------------------------------- MENU --------------------------------------------------

@bot.tree.context_menu(name='Play now')
async def play_now(inter, message: discord.Message):
    ctx = await bot.get_context(inter)
    log(ctx, 'play_now', options=locals(), log_type='command', author=ctx.author)

    if not ctx.interaction.response.is_done():
        await ctx.defer(ephemeral=True)

    if ctx.author.voice is None:
        return await ctx.reply( content=txt(ctx.guild.id, glob, 'You are **not connected** to a voice channel'), ephemeral=True)

    url, probe_data = get_content_of_message(glob, message)
    response: ReturnData = await queue_command_def(ctx, glob, url, mute_response=True, probe_data=probe_data,
                                                   ephemeral=True,
                                                   position=0, from_play=True)
    if not response:
        return

    if response.response:
        return await play_def(ctx, glob, force=True)

    return await ctx.reply(content=response.message, ephemeral=True)

@bot.tree.context_menu(name='Add to queue')
async def add_to_queue(inter, message: discord.Message):
    ctx = await bot.get_context(inter)
    log(ctx, 'add_to_queue', options=locals(), log_type='command', author=ctx.author)

    if not ctx.interaction.response.is_done():
        await ctx.defer(ephemeral=True)

    url, probe_data = get_content_of_message(glob, message)
    response: ReturnData = await queue_command_def(ctx, glob, url, mute_response=True, probe_data=probe_data, ephemeral=True)

    await ctx.reply(content=response.message, ephemeral=True)

# --------------------------------------- GENERAL --------------------------------------------------

@bot.hybrid_command(name='ping', with_app_command=True, description=txt(0, glob, 'command_ping'), help=txt(0, glob, 'command_ping'), extras={'category': 'general'})
async def ping_command(ctx: dc_commands.Context):
    log(ctx, 'ping', options=locals(), log_type='command', author=ctx.author)
    await ping_def(ctx, glob)

# noinspection PyTypeHints
@bot.hybrid_command(name='language', with_app_command=True, description=txt(0, glob, 'command_language'),
                    help=txt(0, glob, 'command_language'), extras={'category': 'general'})
@app_commands.describe(country_code=txt(0, glob, 'attr_language_country_code'))
async def language_command(ctx: dc_commands.Context, country_code: Literal[tuple(languages_dict.keys())]):
    log(ctx, 'language', options=locals(), log_type='command', author=ctx.author)
    await language_command_def(ctx, glob, country_code)

@bot.hybrid_command(name='list', with_app_command=True, description=txt(0, glob, 'command_list'), help=txt(0, glob, 'command_list'), extras={'category': 'general'})
@app_commands.describe(display_type=txt(0, glob, 'attr_list_display_type'), user_only=txt(0, glob, 'ephemeral'))
async def list_command(ctx: dc_commands.Context, display_type: Literal['short', 'medium', 'long']=None, user_only: bool = False):
    log(ctx, 'list', options=locals(), log_type='command', author=ctx.author)
    await list_command_def(ctx, glob, display_type, user_only)


# noinspection PyTypeHints
@bot.hybrid_command(name='options', with_app_command=True, description=txt(0, glob, 'command_options'),
                    help=txt(0, glob, 'command_options'), extras={'category': 'general'})
@app_commands.describe(volume=txt(0, glob, 'attr_options_volume'),
                       buffer=txt(0, glob, 'attr_options_buffer'),
                       language=txt(0, glob, 'attr_options_language'),
                       response_type=txt(0, glob, 'attr_options_response_type'),
                       buttons=txt(0, glob, 'attr_options_buttons'),
                       loop=txt(0, glob, 'attr_options_loop'))
async def options_command(ctx: dc_commands.Context,
                          loop: bool = None,
                          language: Literal[tuple(languages_dict.keys())] = None,
                          response_type: Literal['short', 'long'] = None,
                          buttons: bool = None,
                          volume: discord.ext.commands.Range[int, 0, 200] = None,
                          buffer: discord.ext.commands.Range[int, 5, 3600] = None):
    log(ctx, 'options', options=locals(), log_type='command', author=ctx.author)

    await options_command_def(ctx, glob, loop=loop, language=language, response_type=response_type, buttons=buttons, volume=volume, buffer=buffer)

# ---------------------------------------- ADMIN --------------------------------------------------

async def is_authorised(ctx):
    if ctx.author.id in authorized_users or ctx.author.id == d_id or ctx.author.id == 349164237605568513 or ctx.author.id == config.DEVELOPER_ID:
        return True

@bot.hybrid_command(name='zz_kys', with_app_command=True, hidden=True)
@dc_commands.check(is_authorised)
async def kys(ctx: dc_commands.Context):
    log(ctx, 'kys', options=locals(), log_type='command', author=ctx.author)
    await kys_def(ctx, glob)

# noinspection PyTypeHints
@bot.hybrid_command(name='zz_options', with_app_command=True, hidden=True)
@app_commands.describe(server='all, this, {guild_id}',
                       volume='No division',
                       buffer='In seconds',
                       language='Language code',
                       response_type='short, long',
                       buttons='True, False',
                       loop='True, False')
@dc_commands.check(is_authorised)
async def change_options(ctx: dc_commands.Context,
                         server: discord.ext.commands.GuildConverter = None,
                         stopped: bool = None,
                         loop: bool = None,
                         buttons: bool = None,
                         language: Literal[tuple(languages_dict.keys())] = None,
                         response_type: Literal['short', 'long'] = None,
                         buffer: int = None,
                         volume: int = None):
    log(ctx, 'zz_change_options', options=locals(), log_type='command', author=ctx.author)

    await options_def(ctx, glob,
                      server=str(server),
                      stopped=str(stopped),
                      loop=str(loop),
                      buttons=str(buttons),
                      language=str(language),
                      response_type=str(response_type),
                      buffer=str(buffer),
                      volume=str(volume))

@bot.hybrid_command(name='zz_set_time', with_app_command=True, hidden=True)
@dc_commands.check(is_authorised)
async def set_time_command(ctx: dc_commands.Context, time_stamp: int, ephemeral: bool = True, mute_response: bool = False):
    log(ctx, 'set_time', options=locals(), log_type='command', author=ctx.author)
    await set_video_time(ctx, glob, time_stamp, ephemeral=ephemeral, mute_response=mute_response)

# --------------------------------------------- HELP COMMAND -----------------------------------------------------------

bot.remove_command('help')

@bot.hybrid_command(name='help', with_app_command=True, description=txt(0, glob, 'command_help'), help=txt(0, glob, 'command_help'), extras={'category': 'general'})
async def help_command(ctx: dc_commands.Context, command_name: str = None):
    log(ctx, 'help', options=locals(), log_type='command', author=ctx.author)
    gi = ctx.guild.id

    embed = discord.Embed(title=txt(gi, glob, "Commands"), description=f"{txt(gi, glob, 'Use `/help <command>` to get help on a command')} | Prefix: `{prefix}`")

    command_dict = {}
    command_name_dict = {}
    for command in bot.commands:
        if command.hidden:
            continue

        command_name_dict[command.name] = command

        category = command.extras.get('category', 'No category')
        if category not in command_dict:
            command_dict[category] = []

        command_dict[category].append(command)

    if not command_name:
        for category in command_dict.keys():
            message = ''

            for command in command_dict[category]:
                add = f'`{command.name}` - {txt(gi, glob, command.description)} \n'

                if len(message + add) > 1024:
                    embed.add_field(name=f"**{category.capitalize()}**", value=message, inline=False)
                    message = ''
                    continue

                message = message + add

            embed.add_field(name=f"**{category.capitalize()}**", value=message, inline=False)

        await ctx.send(embed=embed)
        return

    if command_name not in command_name_dict:
        await ctx.send(txt(gi, glob, 'Command not found'))
        return

    command = command_name_dict[command_name]

    embed = discord.Embed(title=command.name, description=txt(gi, glob, command.description))
    # noinspection PyProtectedMember
    for key, value in command.app_command._params.items():
        embed.add_field(name=f"`{key}` - {txt(gi, glob, value.description)}", value=f'{txt(gi, glob, "Required")}: `{value.required}` | {txt(gi, glob, "Default")}: `{value.default}` | {txt(gi, glob, "Type")}: `{value.type}`', inline=False)

    await ctx.send(embed=embed)

# ---------------------------------------------- AUTOCOMPLETE ----------------------------------------------------------

# Local autocomplete functions
@help_command.autocomplete('command_name')
async def help_autocomplete(ctx: discord.Interaction, current: str):
    return await help_autocomplete_def(ctx, current, glob)

@remove.autocomplete('song')
async def song_autocomplete(ctx: discord.Interaction, current: str):
    return await song_autocomplete_def(ctx, current, glob)

@radio_cz_command.autocomplete('radio')
async def radio_autocomplete(ctx: discord.Interaction, current: str):
    return await radio_autocomplete_def(ctx, current, limit=25)

# API request autocomplete functions
@play.autocomplete('query')
async def play_autocomplete(ctx: discord.Interaction, current: str):
    return await query_autocomplete_def(ctx, current, include_youtube=True)

@radio_tunein_command.autocomplete('radio')
async def radio_tunein_autocomplete(ctx: discord.Interaction, current: str):
    return await tunein_autocomplete_def(ctx, current)

@radio_garden_command.autocomplete('radio')
async def radio_garden_autocomplete(ctx: discord.Interaction, current: str):
    return await garden_autocomplete_def(ctx, current)

# --------------------------------------------------- APP --------------------------------------------------------------

if __name__ == '__main__':
    bot.run(config.BOT_TOKEN)
