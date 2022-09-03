from io import BytesIO
from discord import FFmpegPCMAudio
from discord.voice_client import VoiceClient
from pytube import YouTube
from .abstract_player import Player
from .item import Item


class YouTubePlayer(Player):

    def __init__(self, voice_client: VoiceClient) -> None:

        super().__init__(voice_client)
    

    async def play(self, item: Item) -> None:
        yt = YouTube(item.text)
        video = yt.streams.filter(only_audio=True).first()
        buffer = BytesIO()
        video.stream_to_buffer(buffer)
        buffer.seek(0)
        await self.play_wait(FFmpegPCMAudio(executable='ffmpeg',
                                            source=buffer,
                                            pipe=True))