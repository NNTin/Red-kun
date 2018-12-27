from discord.member import VoiceState
from discord.channel import VoiceChannel
from discord import Member, PermissionOverwrite, Embed, Client
from random import choice
from asyncio import Queue
import re
import sys
from redbot.core import Config, checks, commands

# todo: remove the right of changing text/voice channel name directly. Do it via the bot. (Uniform naming between
# todo: channel, voice and role.)
# todo: logging on the specific voice channel (combat join-leave spam -> report to moderator)


class PrivateChannels(commands.Cog):
    """
    have private conservation in a public server
    """
    default_channel = {
        "admin": None,  # first user to join an empty voice channel is admin, he can server mute/deafen
        "textchannel": None,  # a text channel is created and linked to the voice channel
        "role": None,  # a new role is created specific for that text channel, grants reading permission
        "logging": True,  # admin can choose to log (user join/leave, mute/deaf, ...)
    }
    default_guild = {
        "dynamiccategory": None
    }
    conf_id = 800858686
    channel_names = ['antimage', 'axe', 'bane', 'bloodseeker', 'crystal_maiden', 'drow_ranger', 'earthshaker',
                     'juggernaut', 'mirana', 'nevermore', 'morphling', 'phantom_lancer', 'puck', 'pudge', 'razor',
                     'sand_king', 'storm_spirit', 'sven', 'tiny', 'vengefulspirit', 'windrunner', 'zuus', 'kunkka',
                     'lina', 'lich', 'lion', 'shadow_shaman', 'slardar', 'tidehunter', 'witch_doctor', 'riki', 'enigma',
                     'tinker', 'sniper', 'necrolyte', 'warlock', 'beastmaster', 'queenofpain', 'venomancer',
                     'faceless_void', 'skeleton_king', 'death_prophet', 'phantom_assassin', 'pugna', 'templar_assassin',
                     'viper', 'luna', 'dragon_knight', 'dazzle', 'rattletrap', 'leshrac', 'furion', 'life_stealer',
                     'dark_seer', 'clinkz', 'omniknight', 'enchantress', 'huskar', 'night_stalker', 'broodmother',
                     'bounty_hunter', 'weaver', 'jakiro', 'batrider', 'chen', 'spectre', 'doom_bringer',
                     'ancient_apparition', 'ursa', 'spirit_breaker', 'gyrocopter', 'alchemist', 'invoker', 'silencer',
                     'obsidian_destroyer', 'lycan', 'brewmaster', 'shadow_demon', 'lone_druid', 'chaos_knight', 'meepo',
                     'treant', 'ogre_magi', 'undying', 'rubick', 'disruptor', 'nyx_assassin', 'naga_siren',
                     'keeper_of_the_light', 'wisp', 'visage', 'slark', 'medusa', 'troll_warlord', 'centaur',
                     'magnataur', 'shredder', 'bristleback', 'tusk', 'skywrath_mage', 'abaddon', 'elder_titan',
                     'legion_commander', 'ember_spirit', 'earth_spirit', 'terrorblade', 'phoenix', 'oracle', 'techies',
                     'winter_wyvern', 'arc_warden', 'abyssal_underlord', 'monkey_king', 'pangolier', 'dark_willow']

    def __init__(self, bot: Client):
        super().__init__()
        self.bot = bot
        self.config = Config.get_conf(self, self.conf_id)
        self.config.register_channel(**self.default_channel)
        self.config.register_guild(**self.default_guild)
        self.q = Queue()

    @checks.is_owner()
    @commands.command()
    async def pcinit(self, ctx):
        """
        Initializes private channels, run only once
        """
        p = ctx.guild.me.guild_permissions
        if p.manage_channels and p.manage_roles and p.manage_messages:
            category = await ctx.guild.create_category('dynamic room')
            await self.config.guild(ctx.guild).dynamiccategory.set(category.id)
            await ctx.guild.create_voice_channel(name=choice(self.channel_names), category=category)
        else:
            await ctx.send("Bot needs manage roles, manage channels and manage messages permission.")

    async def on_voice_state_update(self, member: Member, before: VoiceState, after: VoiceState):
        if not await self.config.guild(member.guild).dynamiccategory():
            # do nothing, user needs to run 'pcinit' to make use of this cog
            return

        # todo: uncomment when this feature is more polished
        # await self.state_change(member, before, after)

        # ensuring methods are ran only one at a time with a queue
        if before.channel != after.channel:
            await self.q.put((self.check_voice_channel(before.channel, member), before.channel))
            await self.q.put((self.check_voice_channel( after.channel, member), after.channel))

    async def workqueue(self):
        # ensuring methods are ran only one at a time with a queue
        while True:
            try:
                await_this, channel = await self.q.get()
                await await_this
            except:
                print(sys.exc_info([0]))

    async def state_change(self, member: Member, before: VoiceState, after: VoiceState):
        if before.deaf != after.deaf:
            await self.log_message(member, after.channel, 'guild deaf' if after.deaf else 'guild undeaf')
        if before.mute != after.mute:
            await self.log_message(member, after.channel, 'guild mute' if after.mute else 'guild unmute')
        if before.self_mute != after.self_mute:
            await self.log_message(member, after.channel, 'self mute' if after.self_mute else 'self unmute')
        if before.self_deaf != after.self_deaf:
            await self.log_message(member, after.channel, 'self deaf' if after.self_deaf else 'self undeaf')
        if before.channel != after.channel:
            await self.log_message(member, before.channel, 'user left')
            await self.log_message(member, after.channel, 'user joined')

    async def log_message(self, member: Member, channel: VoiceChannel, message: str):
        if not channel:
            # can't log if channel does not exist
            return

        channel_group = self.config.channel(channel)
        if not await channel_group():
            # do nothing if config doesn't exist
            return

        if not await channel_group.logging():
            # don't log when logging is diabled
            return

        text_channel = self.bot.get_channel(id=await channel_group.textchannel())
        if not text_channel:
            # can't log if channel does not exist
            return

        embed = Embed(description='{}'.format(member.mention))
        embed.set_author(icon_url=member.avatar_url_as(), name=message)
        embed.set_footer(text='NNTin cogs', icon_url='https://i.imgur.com/6LfN4cd.png')

        await text_channel.send(embed=embed)

    async def check_voice_channel(self, voice_channel: VoiceChannel, member: Member):
        # voice channel does not exist, do nothing
        if not voice_channel:
            return

        guild_group = self.config.guild(voice_channel.guild)

        # voice channel is not dynamic, do nothing
        if voice_channel.category_id != await guild_group.dynamiccategory():
            return

        channel_group = self.config.channel(voice_channel)

        if len(voice_channel.members) == 0:
            # restore default config, destroy text channel, destroy role
            # reset admin
            await channel_group.admin.set(None)

            # reset channel
            text_channel = self.bot.get_channel(id=await channel_group.textchannel())
            await channel_group.textchannel.set(None)
            if text_channel:
                await text_channel.delete()

            # reset role
            role_id = await channel_group.role()
            for role in voice_channel.guild.roles:
                if role.id == role_id:
                    await role.delete()
            await channel_group.role.set(None)

            # delete voice channel
            if voice_channel:
                try:
                    await voice_channel.delete()
                except:
                    pass

        else:
            if len(voice_channel.members) == 1:
                # check if there is already an admin
                if not await channel_group.admin():
                    admin = voice_channel.members[0]

                    # set admin
                    await channel_group.admin.set(admin.id)

                    # create text channel
                    overwrites = {
                        voice_channel.guild.default_role: PermissionOverwrite(read_messages=False),
                        voice_channel.guild.me: PermissionOverwrite(read_messages=True)
                    }
                    category_id = await guild_group.dynamiccategory()
                    category = self.bot.get_channel(id=category_id)
                    text_channel = await voice_channel.guild.create_text_channel(name=re.sub(r'\W+', '', voice_channel.name),
                                                                                 category=category, overwrites=overwrites)

                    await channel_group.textchannel.set(text_channel.id)

                    # basic announcement
                    embed = Embed(description='{} joined the voice channel first and thus has elevated privileges. '
                                              'He/she can delete messages in this text channel as well as change '
                                              'the text/voice channel names. Furthermore if desired he/she can '
                                              'set a user limit on the voice channel to ensure no one else interrupts '
                                              'your privacy.'.format(admin.mention),
                                  color=member.color)
                    embed.set_author(icon_url=admin.avatar_url_as(), name="Announcement")
                    embed.add_field(name='How does this work?',
                                    value='People in the same voice channel share a role. That role grants '
                                          'access to this text channel. The first person to join a voice channel '
                                          'has elevated privileges. Once a voice channel is empty the text'
                                          'channel is deleted.',
                                    inline=False)
                    embed.add_field(name='Why?',
                                    value='To give you a little bit of privacy among your close friends.',
                                    inline=False)
                    embed.add_field(name='Warning',
                                    value='With great power comes great responsibility. Moderators reserve the right '
                                          'to ban you from the server if you choose to rename your voice and text '
                                          'channels to offensive names or practice otherwise obnoxious behavior.\n'
                                          'Although you have a private discussion platform **rules still apply!**',
                                    inline=False)
                    embed.set_footer(text='NNTin cogs', icon_url='https://i.imgur.com/6LfN4cd.png')
                    await text_channel.send(embed=embed)

                    # create role
                    role = await voice_channel.guild.create_role(name=re.sub(r'\W+', '', voice_channel.name),
                                                                 mentionable=True)
                    await channel_group.role.set(role.id)

                    # Overwrites for people with the role
                    # people with the role (same voice channel) can see the hidden text channel
                    overwrite = PermissionOverwrite()
                    overwrite.read_messages = True
                    await text_channel.set_permissions(target=role, overwrite=overwrite)

                    # Admin of the voice and text channel
                    # Text channel
                    overwrite = PermissionOverwrite()
                    overwrite.manage_messages = True
                    overwrite.manage_channels = True
                    await text_channel.set_permissions(target=admin, overwrite=overwrite)
                    # Voice channel
                    overwrite = PermissionOverwrite()
                    overwrite.manage_channels = True
                    await voice_channel.set_permissions(target=admin, overwrite=overwrite)

                    # create new empty voice channel for other to use
                    await voice_channel.guild.create_voice_channel(name=choice(self.channel_names), category=category)

            # set/take role from members
            role_id = await channel_group.role()
            for role in voice_channel.guild.roles:
                if role.id == role_id:
                    if member in voice_channel.members:
                        await member.add_roles(role)
                    else:
                        # take away role
                        await member.remove_roles(role)



