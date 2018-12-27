from .privatechannels import PrivateChannels
from redbot.core.bot import Red
import asyncio


async def setup(bot: Red):
    cog = PrivateChannels(bot)
    #bot.add_listener(n.voice_state_update, "on_voice_state_update")
    loop = asyncio.get_event_loop()
    loop.create_task(cog.workqueue())
    bot.add_cog(cog)