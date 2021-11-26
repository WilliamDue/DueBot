import io
import asyncio
import ffmpegfix
from gtts import gTTS
from discord.errors import ClientException
from discord.voice_client import VoiceClient
from discord.ext.commands.context import Context

async def init_voice_client(ctx: Context) -> VoiceClient:
    
    if ctx.author.voice is None:
        await ctx.send('You are not in a voice channel, so this command cannot be used.')
        return
    
    channel = ctx.author.voice.channel
    voice_client = ctx.guild.voice_client

    if voice_client is None:
        voice_client = await channel.connect()

    if voice_client is not None and channel.id != ctx.voice_client.channel.id:
        await voice_client.disconnect()
        voice_client = await channel.connect()
    
    return voice_client

async def play_tts(ctx: Context, text: str) -> None:
    
    voice_client = await init_voice_client(ctx)
    
    text_segments = [n for n in text.split('.')]
    truth_values = map(lambda x : len(x) <= 2048, text_segments)
    
    if not any(truth_values):
        await ctx.send('Some sentences were too long, they were over 2048 chars.')
        return
    
    playlist = []
    
    def is_error_on_play() -> bool:
        try:
            if not voice_client.is_playing():
                fp = playlist.pop()
                voice_client.play(ffmpegfix.FFmpegPCMAudio(executable='ffmpeg',
                                                           source=fp.read(),
                                                           pipe=True))
                fp.close()
        except ClientException:
            return True
        return False
    
    for segment in text_segments:
        
        fp = io.BytesIO()
        try:
            gTTS(text=segment, lang='en', slow=False).write_to_fp(fp)
        except AssertionError:
            continue
        
        fp.seek(0)
        playlist.append(fp)
        
        if is_error_on_play():
            return
        
        await asyncio.sleep(.1)
        
    while len(playlist) > 0:
        
        if is_error_on_play():
            return
        
        await asyncio.sleep(.1)