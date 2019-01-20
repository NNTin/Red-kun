from .presence import Presence
from redbot.core.bot import Red


async def setup(bot: Red):
    cog = Presence(bot)
    bot.add_cog(cog)
    bot.add_listener(cog._on_member_update, "on_member_update")
