#!/usr/bin/python3

import sys
import discord
import voice
import scraping
from discord.ext import commands
from discord.ext.commands.context import Context
from discord.ext.commands.converter import MessageConverter
from discord.utils import get

FFMPEG_OPTIONS = {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
        'options': '-vn -loglevel fatal',
    }

bot = commands.Bot(command_prefix='&')

@bot.command(name='kill', aliases=['leave', 'k'], help="Stops bot in voice channels")
async def kill(ctx : Context) -> None:
    channel = get(bot.voice_clients, guild=ctx.guild)

    if channel is None:
        return
    
    await channel.disconnect()

@bot.command(pass_context=True)
async def tts(ctx: Context, *, message : str) -> None:
    
    await voice.play_tts(ctx, message)
        
@bot.command(pass_context=True)
async def literotica(ctx: Context, *, link : str) -> None:
    
    text = scraping.get_literotica_text(link)
    
    bot.loop.create_task(voice.play_tts(ctx, text))

@bot.command(name='bruh', aliases=['david'], help='Says bruh.')
async def bruh(ctx : Context) -> None:
    
    voice_client = await voice.init_voice_client(ctx)
    
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