from discord import Embed
from redbot.core import commands


class ExtendedEmbed(Embed):
    """An extended discord.Embed class"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_footer(text='NNTin cogs', icon_url='https://i.imgur.com/6LfN4cd.png')


def check_allow_subscription_and_not_enable_default():
    async def check(ctx: commands.Context):
        if not ctx.guild:
            return False
        cog = ctx.bot.get_cog("Presence")
        if not cog:
            return False
        return (await cog.config.guild(ctx.guild).allow_subscription() and
                not await cog.config.guild(ctx.guild).enable_default())
    return commands.check(check)
