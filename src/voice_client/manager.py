from discord.voice_client import VoiceClient
from discord.ext.commands.context import Context
from typing import Dict
from players import Player
from .queue import VoiceClientQueue


class VoiceClientManager:

    def __init__(self):
        self.voice_client_queues: Dict[int, VoiceClientQueue] = dict()
    

    async def delete(self, guild_id: int) -> None:
        queue = self.voice_client_queues.pop(guild_id, None)

        if queue is not None:
            await queue.stop()
    

    async def skip(self, guild_id: int) -> None:
        queue = self.voice_client_queues[guild_id]

        if queue is not None:
            await queue.skip()
    

    async def update(self, guild_id: int, voice_client: VoiceClient) -> None:
        queue = self.voice_client_queues.get(guild_id)

        if queue is None:
            return

        await queue.update(voice_client)
    

    async def init_voice_client(self, ctx: Context) -> VoiceClient:
        if ctx.author.voice is None:
            return None
        
        channel = ctx.author.voice.channel
        voice_client = ctx.guild.voice_client

        if voice_client is None:
            voice_client = await channel.connect()

        if voice_client is not None and channel.id != ctx.voice_client.channel.id:
            await voice_client.disconnect()
            voice_client = await channel.connect()
        
        return voice_client


    async def get(self, ctx: Context) -> VoiceClientQueue:
        voice_client = await self.init_voice_client(ctx)

        if voice_client is None:
            return None
        
        queue = self.voice_client_queues.get(ctx.guild.id)
        if queue is None:
            queue = VoiceClientQueue(voice_client)
            self.voice_client_queues[ctx.guild.id] = queue
        
        return queue
    

    async def try_push(self, player: Player) -> None:
        queue = await self.get(player.context)

        can_play = queue is not None
        if can_play:
            await queue.push(player)
        
        return can_play
    

    def get_page(self, guild_id: int, page: int):
        queue = self.voice_client_queues.get(guild_id)
        if queue is None:
            return []
        
        return queue.get_page(page) 
