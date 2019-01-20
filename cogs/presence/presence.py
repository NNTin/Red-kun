from discord import Member, Role, Status
from .helper import ExtendedEmbed as Embed
from .helper import check_allow_subscription_and_not_enable_default
from redbot.core import Config, commands
from redbot.core import checks
from redbot.core.bot import Red
from redbot.core.utils.chat_formatting import pagify
from redbot.core.commands import Context


class Presence(commands.Cog):
    """
    Dynamically give out roles depending on the presence/status of server members.
    """

    default_guild = {
        "status": {
            "online": None,             # online status
            "idle": None,               # idle status
            "do_not_disturb": None,     # do not disturb status
            "offline": None             # offline or invisible status
        },
        "enable_default": True,         # whether the roles are given out to everyone in the guild
        "members": [],                  # ^ if not: collection of members where the role is given out
        "allow_subscription": True      # whether guild members can sign up
    }
    conf_id = 800858686

    def __init__(self, bot: Red):
        super().__init__()
        self.bot = bot
        self.config = Config.get_conf(self, self.conf_id)
        self.config.register_guild(**self.default_guild)

    @commands.group()
    async def presence(self, ctx):
        """
        Dynamically giving out roles depending on the presence/status of server members.
        """
        pass

    if True:  # set/reset roles
        @presence.command()
        async def set(self, ctx, status: str, role: Role):
            """
            Automatically assign a role when a user's status becomes `online`, `idle`, `do_not_disturb`, `offline`

            Syntax:
                [p]presence set idle @role_idle
            """
            async with self.config.guild(ctx.guild)() as guild_group:
                if status in guild_group["status"].keys():
                    guild_group["status"][status] = role.id
                    embed = Embed(title="Success",
                                  description="Status role successfully set.")
                else:
                    embed = Embed(
                        title="Error",
                        description=f"{status} is not a valid status.\n"
                        f"Valid statuses are: `online`, `idle`, `do_not_disturb`, `offline`"
                    )
                await ctx.send(embed=embed)

        @presence.command()
        async def reset(self, ctx, status: str):
            """
            Stop assigning a role when a user's status becomes `online`, `idle`, `do_not_disturb`, `offline`

            Syntax:
                [p]presence reset idle
            """
            async with self.config.guild(ctx.guild)() as guild_group:
                if status in guild_group["status"].keys():
                    guild_group["status"][status] = None
                    embed = Embed(title="Success",
                                  description="Status role successfully reset.")
                else:
                    embed = Embed(
                        title="Error",
                        description=f"{status} is not a valid status.\n"
                        f"Valid statuses are: `online`, `idle`, `do_not_disturb`, `offline`"
                    )
                await ctx.send(embed=embed)

    if True:  # add/remove
        @checks.admin_or_permissions(manage_roles=True)
        @presence.command()
        async def add(self, ctx, member: Member):
            """
            Add dynamic role distribution to a Discord member.

            Syntax:
                [p]presence add @Linley#8686
            """
            async with self.config.guild(ctx.guild)() as guild_group:
                if member.id in guild_group["members"]:
                    embed = Embed(title="Error", description=f"{member.mention} is already in the list.")
                else:
                    guild_group["members"].append(member.id)
                    embed = Embed(title="Success", description=f"{member.mention} added to the list.")
                if guild_group["enable_default"]:
                    embed.add_field(name="Warning", value="Status role is given to all guild members by default.\n"
                                                          "Do `[p]presence toggle_default` if this is not desired.")
                elif guild_group["allow_subscription"]:
                    embed.add_field(name="Info", value="Your guild members can sign up themselves by using the command:"
                                                       "`[p]presence subscribe`\n"
                                                       "Do `[p]presence toggle_allow_subscription` if this is not desired.")
            await ctx.send(embed=embed)
            await self._update(member)

        @checks.admin_or_permissions(manage_roles=True)
        @presence.command()
        async def remove(self, ctx, member: Member):
            """
            Remove dynamic role distribution from a Discord member.

            Syntax:
                [p]presence remove @Linley#8686
            """
            async with self.config.guild(ctx.guild)() as guild_group:
                if member.id in guild_group["members"]:
                    guild_group["members"].remove(member.id)
                    embed = Embed(title="Success", description=f"{member.mention} has successfully been removed.")
                else:
                    embed = Embed(title="Error", description=f"{member.mention} wasn't in the list.")
            await ctx.send(embed=embed)
            await self._clear_dynamic_roles(member)

    if True:  # subscribe/unsubscribe
        @check_allow_subscription_and_not_enable_default()
        @presence.command()
        async def subscribe(self, ctx):
            """
            Subscribe to the dynamic role

            Syntax:
                [p]presence subscribe
            """
            async with self.config.guild(ctx.guild)() as guild_group:
                if ctx.author.id in guild_group["members"]:
                    embed = Embed(title="Error", description=f"{ctx.author.mention}, you are already subscribed.")
                else:
                    guild_group["members"].append(ctx.author.id)
                    embed = Embed(
                        title="Success",
                        description=f"{ctx.author.mention}, you will be given roles "
                        f"depending on your current status."
                    )
            await ctx.send(embed=embed)
            await self._update(ctx.author)

        @check_allow_subscription_and_not_enable_default()
        @presence.command()
        async def unsubscribe(self, ctx):
            """
            Unsubscribe from the dynamic role

            Syntax:
                [p]presence unsubscribe
            """
            async with self.config.guild(ctx.guild)() as guild_group:
                if ctx.author.id in guild_group["members"]:
                    guild_group["members"].remove(ctx.author.id)
                    embed = Embed(
                        title="Success",
                        description=f"{ctx.author.mention}, you will no longer be given roles "
                        f"depending on your current status."
                    )
                else:
                    embed = Embed(
                        title="Error", description=f"{ctx.author.mention}, you can't unsubscribe if you aren't subscribed."
                    )
            await ctx.send(embed=embed)
            await self._clear_dynamic_roles(ctx.author)

    if True:  # toggle
        @checks.admin_or_permissions(manage_roles=True)
        @presence.command()
        async def toggle_default(self, ctx):
            """
            Toggle whether status roles should be automatically given out to everyone or explicitly subscribed users.
            """
            async with self.config.guild(ctx.guild)() as guild_group:
                guild_group["enable_default"] = not guild_group["enable_default"]
                if guild_group["enable_default"]:
                    embed = Embed(title="Success", description="The status roles will be given out to everyone."
                                                               "Due to rate limiting this does not work retro-actively.")
                else:
                    embed = Embed(title="Success", description="The status roles will now only be given to explicitly "
                                                               "subscribed or added users. It is recommended that you "
                                                               "create new clean roles since already given out roles "
                                                               "will not be removed.")   # todo....
            await ctx.send(embed=embed)

        @checks.admin_or_permissions(manage_roles=True)
        @presence.command()
        async def toggle_allow_subscription(self, ctx):
            """
            Toggle whether the users are allowed to subscribe/unsubscribe to those dynamic roles.
            """
            async with self.config.guild(ctx.guild)() as guild_group:
                guild_group["allow_subscription"] = not guild_group["allow_subscription"]
                if guild_group["allow_subscription"]:
                    embed = Embed(title="Success", description="Your discord members can manually subscribe/unsubscribe "
                                                               "to the status roles.")
                    embed = Embed(title="Success", description="Your discord members can no longer subscribe/unsubscribe.")
            await ctx.send(embed=embed)

    if True:  # misc
        @checks.admin_or_permissions(manage_roles=True)
        @presence.command()
        async def list_members(self, ctx):
            """
            List the subscribed members
            """
            async with self.config.guild(ctx.guild)() as guild_group:
                msg = ["<@" + str(member) + ">" for member in guild_group["members"]]
                msg = "\n".join(msg)
                if msg:
                    for page in pagify(text=msg, shorten_by=50):
                        await ctx.send(embed=Embed(title="Subscribed members", description=page))
                else:
                    embed = Embed(title="Error", description="No members added.")
                    if guild_group["enable_default"]:
                        embed.add_field(name="Warning", value="Status role is given to all guild members by default.\n"
                                                              "Do `[p]presence toggle_default` if this is not desired.")
                    elif guild_group["allow_subscription"]:
                        embed.add_field(name="Info",
                                        value="Your guild members can sign up themselves by using the command:"
                                              "`[p]presence subscribe`\n"
                                              "Do `[p]presence toggle_allow_subscription` if this is not desired.")
                    await ctx.send(embed=embed)

        async def _on_member_update(self, before: Member, after: Member):
            await self._update(after)

    async def _update(self, member: Member):
        """
        Actual logic behind giving and removing roles.
        """
        async with self.config.guild(member.guild)() as guild_group:
            if guild_group["enable_default"] or member.id in guild_group["members"]:
                for key, value in guild_group["status"].items():
                    if value:
                        role = member.guild.get_role(value)
                        if key == "online":
                            status = Status.online
                        elif key == "idle":
                            status = Status.idle
                        elif key == "do_not_disturb":
                            status = Status.do_not_disturb
                        else:
                            status = Status.offline

                        if member.status == status:
                            if role not in member.roles:
                                await member.add_roles(role)
                        else:
                            if role in member.roles:
                                await member.remove_roles(role)

    async def _clear_dynamic_roles(self, member: Member):
        """
        Clear their dynamic roles.
        """
        async with self.config.guild(member.guild)() as guild_group:
            for key, value in guild_group["status"].items():
                if value:
                    role = member.guild.get_role(value)
                    if role in member.roles:
                        await member.remove_roles(role)
