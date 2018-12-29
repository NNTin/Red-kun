from .icu import ICU
from redbot.core.bot import Red


async def setup(bot: Red):
    cog = ICU(bot)
    bot.add_cog(cog)
