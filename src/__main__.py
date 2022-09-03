from discord.ext import commands
from cogs import VoiceClientCog
import sys
import discord


bot = commands.Bot(command_prefix='&', intents=discord.Intents.all())


@bot.event
async def on_ready():
    await bot.add_cog(VoiceClientCog(bot))

    
def get_key() -> str:
    for line in sys.stdin:
        return line


def main():
    bot.run(get_key())


if __name__ == '__main__':
    main()