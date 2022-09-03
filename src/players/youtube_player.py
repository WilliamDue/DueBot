from io import BytesIO
from discord import FFmpegPCMAudio
from discord.voice_client import VoiceClient
from pytube import YouTube
from .abstract_player import Player
from discord.ext.commands.context import Context


class YouTubePlayer(Player):

    def __init__(self, text: str, context: Context) -> None:
        super().__init__(text, context)
    

    async def play(self, voice_client: VoiceClient) -> None:
        yt = YouTube(self.text)
        video = yt.streams.filter(only_audio=True).first()
        buffer = BytesIO()
        video.stream_to_buffer(buffer)
        buffer.seek(0)
        await self.play_wait(
            voice_client,
            FFmpegPCMAudio(
                executable='ffmpeg',
                source=buffer,
                pipe=True
            )
        )