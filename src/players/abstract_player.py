from abc import ABC, abstractmethod
from discord.ext.commands.context import Context
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, List
from discord import AudioSource
from discord.voice_client import VoiceClient
from .audio_sources.ffmpegfix import FFmpegPCMAudio
from io import BytesIO
import asyncio


class Player(ABC):

    def __init__(self, text: str, context: Context) -> None:
        self.text = text
        self.context = context
        self.is_playing = False


    @abstractmethod
    async def play(self, voice_client: VoiceClient) -> None:
        raise NotImplementedError
    

    def after(self, error) -> None:
        self.is_playing = False
    

    async def play_wait(self, voice_client: VoiceClient, source: AudioSource) -> None:
        self.is_playing = True
        voice_client.play(source, after=self.after)
        while self.is_playing:
            await asyncio.sleep(.1)
    

    async def lazy_play_wait(
            self,
            voice_client: VoiceClient,
            func: Callable[[object], BytesIO],
            objects: List[object]
        ) -> None:
        with ThreadPoolExecutor(max_workers=1) as executor:
            for fp in executor.map(func, objects, timeout=15):
                if fp is None:
                    continue

                if not voice_client.is_connected():
                    break
                
                with fp:
                    await self.play_wait(
                        voice_client,
                        FFmpegPCMAudio(
                            executable='ffmpeg',
                            source=fp.read(),
                            pipe=True
                        )
                    )
