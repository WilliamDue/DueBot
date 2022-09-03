from .abstract_player import Player
from discord import FFmpegPCMAudio
from discord.voice_client import VoiceClient
from discord.ext.commands.context import Context


class FilePlayer(Player):

    def __init__(self, text: str, context: Context) -> None:
        super().__init__(text, context)


    async def play(self, voice_client: VoiceClient) -> None:
        await self.play_wait(
            voice_client,
            FFmpegPCMAudio(
                executable='ffmpeg',
                source=self.text
            )
        )