#!/usr/bin/python3

import sys
import discord
import scraping
from discord.ext import commands
from discord.ext.commands.context import Context
from discord.voice_client import VoiceClient
from discord.utils import get
from tts import TTS, TTSQueue


bot = commands.Bot(command_prefix='&')
tts_queue = TTSQueue()
bot.loop.create_task(tts_queue.run())


async def init_voice_client(ctx: Context) -> VoiceClient:
    
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


@bot.command(name='kill', aliases=['leave', 'k'], help="Stops bot in voice channels.")
async def kill(ctx : Context) -> None:
    channel = get(bot.voice_clients, guild=ctx.guild)

    if channel is None:
        return
    
    await channel.disconnect()


@bot.command(pass_context=True)
async def tts(ctx: Context, *, text: str) -> None:
    voice_client = await init_voice_client(ctx)

    if voice_client is None:
        await ctx.send('You are not in a voice channel, so this command cannot be used.')
        return
    
    await tts_queue.push(text, voice_client)
    
        
@bot.command(pass_context=True)
async def literotica(ctx: Context, *, link: str) -> None:
    text = scraping.get_literotica_text(link)
    voice_client = await init_voice_client(ctx)

    if voice_client is None:
        await ctx.send('You are not in a voice channel, so this command cannot be used.')
        return
    
    await tts_queue.push(text, voice_client)
    

@bot.command(name='bruh', aliases=['david'], help='Says bruh.')
async def bruh(ctx : Context) -> None:
    
    voice_client = await init_voice_client(ctx)
    
    filename = './bruh.mp4'
    
    voice_client.play(discord.FFmpegPCMAudio(executable='ffmpeg',
                                             source=filename))

def get_key() -> str:
    for line in sys.stdin:
        return line

def main():
    bot.run(get_key())

if __name__ == '__main__':
    main()