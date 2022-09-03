from .abstract_player import Player
from discord import FFmpegPCMAudio
from discord.voice_client import VoiceClient
from .item import Item


class FilePlayer(Player):

    def __init__(self, voice_client: VoiceClient) -> None:
        super().__init__(voice_client)
    

    async def play(self, item: Item) -> None:
        await self.play_wait(FFmpegPCMAudio(executable='ffmpeg',
                                            source=item.text))