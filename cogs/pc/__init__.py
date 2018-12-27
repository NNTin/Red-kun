from .privatechannels import PrivateChannels
from redbot.core.bot import Red
import asyncio


async def setup(bot: Red):
    cog = PrivateChannels(bot)
    loop = asyncio.get_event_loop()
    loop.create_task(cog.workqueue())
    bot.add_cog(cog)
