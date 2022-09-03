from discord.voice_client import VoiceClient
from discord.ext import tasks
from typing import Callable, Dict, List
from players import TTSPlayer, FilePlayer, Player, PlayerType, YouTubePlayer, Item
import asyncio

from players.literotica_player import LiteroticaPlayer


class VoiceClientQueue:

    def __init__(
            self,
            voice_client: VoiceClient,
            players: Dict[PlayerType, Callable[[VoiceClient], Player]] = None
        ) -> None:
        self.queue: List[Item] = []

        if players is None:
            self.players = {
                PlayerType.File: FilePlayer(voice_client),
                PlayerType.TTS: TTSPlayer(voice_client),
                PlayerType.YouTube: YouTubePlayer(voice_client),
                PlayerType.Literotica: LiteroticaPlayer(voice_client)
            }
        else:
            self.players = dict()
            for key, val in players:
                self.players[key] = val(voice_client)

        self.listen.start()
        self.active = None
        self.coro = None

    
    async def push(self, player_type: PlayerType, item: Item) -> None:
        self.queue.append((player_type, item))
    

    async def update(self, voice_client) -> None:
        await Player.update(voice_client, self.players.values)


    @tasks.loop(seconds=0.1)
    async def listen(self) -> None:
        if self.coro is not None:
            await asyncio.wait({self.coro})
            self.coro = None
            self.item = None

        try:
            player_type, item = self.queue.pop()
        except IndexError:
            return

        self.coro = asyncio.create_task(self.players[player_type].play(item))
        self.item = item
    

    async def skip(self) -> None:
        if self.coro is None:
            return
        
        self.coro.cancel()
        Player.stop(self.players.values())


    async def stop(self) -> None:
        await self.skip()
        self.listen.stop()
    
    
    def get_page(self, page: int) -> List[Item]:
        if page == 0:
            temp = [self.item]
            temp.extend(self.queue[:4])
            return temp
        
        start = page * 5 + 1
        end = (page + 1) * 5 + 1
        
        return self.queue[start:end]