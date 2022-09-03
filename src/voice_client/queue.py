from discord.voice_client import VoiceClient
from discord.ext import tasks
from typing import List
from players import Player
import asyncio


class VoiceClientQueue:

    def __init__(
            self,
            voice_client: VoiceClient,
        ) -> None:
        self.queue: List[Player] = []
        self.voice_client = voice_client
        self.listen.start()
        self.player = None
        self.coro = None

    
    async def push(self, player: Player) -> None:
        self.queue.append(player)
    

    async def update(self, voice_client) -> None:
        await Player.update(voice_client, self.players.values)


    @tasks.loop(seconds=0.1)
    async def listen(self) -> None:
        if self.coro is not None:
            await asyncio.wait({self.coro})
            self.coro = None
            self.player = None

        try:
            player = self.queue.pop()
        except IndexError:
            return

        self.coro = asyncio.create_task(player.play(self.voice_client))
        self.player = player
    

    async def skip(self) -> None:
        if self.coro is None:
            return
        
        self.coro.cancel()
        self.voice_client.stop()


    async def stop(self) -> None:
        await self.skip()
        self.listen.stop()
    
    
    def get_page(self, page: int) -> List[Player]:
        if page == 0:
            temp = [self.player]
            temp.extend(self.queue[:4])
            return temp
        
        start = page * 5 + 1
        end = (page + 1) * 5 + 1
        
        return self.queue[start:end]