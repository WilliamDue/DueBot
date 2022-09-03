from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, List
from discord import AudioSource
from discord.voice_client import VoiceClient
from .audio_sources.ffmpegfix import FFmpegPCMAudio
from .item import Item
from io import BytesIO
import asyncio


class Player(ABC):

    def __init__(self, voice_client: VoiceClient) -> None:
        self.voice_client = voice_client
        self.is_playing = False
        super().__init__()


    @abstractmethod
    async def play(self, item: Item) -> None:
        raise NotImplementedError
    

    async def update(self, voice_client: VoiceClient) -> None:
        self.voice_client = voice_client
    

    def after(self, error) -> None:
        self.is_playing = False
    

    async def play_wait(self, source: AudioSource) -> None:
        self.is_playing = True
        self.voice_client.play(source, after=self.after)
        while self.is_playing:
            await asyncio.sleep(.1)
    

    async def lazy_play_wait(self, func: Callable[[object], BytesIO], objects: List[object]) -> None:
        with ThreadPoolExecutor(max_workers=1) as executor:
            for fp in executor.map(func, objects, timeout=15):
                if fp is None:
                    continue

                if not self.voice_client.is_connected():
                    break
                
                with fp:
                    await self.play_wait(FFmpegPCMAudio(executable='ffmpeg',
                                                        source=fp.read(),
                                                        pipe=True))
    

    @staticmethod
    async def update(voice_client: VoiceClient, players: list) -> None:
        for player in players:
            await player.update(voice_client)


    @staticmethod
    def stop(players: list) -> None:
        for player in players:
            if player.voice_client.is_playing():
                player.voice_client.stop()