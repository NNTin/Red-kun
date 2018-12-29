from discord import Member, Embed, Role, Message
from discord.errors import Forbidden
from typing import Union
from redbot.core import Config, checks, commands
from redbot.core.bot import Red
from redbot.core.commands import Context


class ICU(commands.Cog):
    """
    Teach a valuable lesson about pinging @everyone and @here.
    Or hand out custom roles for pinging certain users.
    """

    # role_assignation: pinged_victim_id -> given_role_id
    default_guild = {
        "member_mention": {},
        "role_mention": {}
    }
    conf_id = 800858686

    def __init__(self, bot: Red):
        super().__init__()
        self.bot = bot
        self.config = Config.get_conf(self, self.conf_id)
        self.config.register_guild(**self.default_guild)

    async def on_message(self, message: Message):
        # This cog only cares about messages with mentions
        if not message.mentions and not message.role_mentions:
            return

        guild_group = self.config.guild(message.guild)
        role = None

        async with guild_group.member_mention() as member_mention:
            for mention in message.mentions:
                if str(mention.id) in member_mention.keys():
                    role = message.guild.get_role(member_mention[str(mention.id)])

        async with guild_group.role_mention() as role_mention:
            for mention in message.role_mentions:
                if str(mention.id) in role_mention.keys():
                    role = message.guild.get_role(role_mention[str(mention.id)])
        if role:
            try:
                await message.author.add_roles(role)
            except Forbidden:
                print("Bot could not assign role. Lacking permission.\n"
                      "Guild: {}\n"
                      "Member: {}\n"
                      "Role: {}".format(message.guild.id, message.author.id, role.id))

    @checks.is_owner()
    @commands.group()
    async def icu(self, ctx):
        """
        Configuration for icu
        """
        pass

    @icu.command()
    async def reset(self, ctx: Context, pinged_victim: Union[Role, Member]):
        """
        Stop handing out roles for pinging certain users or roles.

        Syntax:
            [p]icu reset @moderator
        """
        guild_group = self.config.guild(ctx.guild)
        _id = None
        if isinstance(pinged_victim, Role):
            async with guild_group.role_mention() as role_mention:
                _id = role_mention.pop(str(pinged_victim.id), None)
        elif isinstance(pinged_victim, Member):
            async with guild_group.member_mention() as member_mention:
                _id = member_mention.pop(str(pinged_victim.id), None)

        embed = None
        if _id:
            role = ctx.guild.get_role(_id)
            embed = Embed(color=pinged_victim.color, title="Ping rule removed",
                          description="The {} role will no longer be given out for pinging {}".format(
                              role.mention, pinged_victim.mention
                          ))
        else:
            embed = Embed(color=pinged_victim.color, title="Error",
                          description="{} has no ping rule defined.".format(pinged_victim.mention))
        embed.set_footer(text='NNTin cogs', icon_url='https://i.imgur.com/6LfN4cd.png')
        await ctx.send(embed=embed)

    @icu.command()
    async def set(self, ctx: Context, pinged_victim: Union[Role, Member], given_role: Role):
        """
        Set up the icu cog.

        Syntax:
            [p]icu set \@everyone \@everyone
            whereas \@everyone being a custom made role named everyone - a fake @everyone.
            [p]icu set @moderator @alerter
            when @moderator is pinged the user is given the @alerter role.
            [p]icu set @Linley#8686 @warn
            when @Linley#8686 is pinged the user is given the @warn role.
        """
        guild_group = self.config.guild(ctx.guild)
        if isinstance(pinged_victim, Role):
            async with guild_group.role_mention() as role_mention:
                role_mention[pinged_victim.id] = given_role.id
        elif isinstance(pinged_victim, Member):
            async with guild_group.member_mention() as member_mention:
                member_mention[pinged_victim.id] = given_role.id

        embed = Embed(color=given_role.color, title="Ping rule added",
                      description="Users who ping {} will be given the {} role.".format(
                          pinged_victim.mention, given_role.mention
                      ))
        embed.set_footer(text='NNTin cogs', icon_url='https://i.imgur.com/6LfN4cd.png')
        await ctx.send(embed=embed)
