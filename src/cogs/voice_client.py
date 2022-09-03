from discord.ext.commands import Bot, Cog, command, group
from discord.ext.commands.context import Context
from discord.member import Member, VoiceState
from discord.utils import get
from voice_client import VoiceClientManager
from discord import ButtonStyle, Interaction
from discord.ui import View, Button, button
from players import TTSPlayer, LiteroticaPlayer, FilePlayer, YouTubePlayer


class QueueView(View):

    def __init__(self, manager: VoiceClientManager, *, timeout=180):
        self.page = 0
        self.manager = manager
        super().__init__(timeout=timeout)

    
    @button(label='⬅️', style=ButtonStyle.gray)
    async def left_button(self, interaction: Interaction, button: Button):
        self.page = max(0, self.page - 1)
        pages = self.manager.get_page(interaction.guild_id, self.page)
        await interaction.response.edit_message(content=self.format_queue(pages))
    

    @button(label='➡️', style=ButtonStyle.gray)
    async def right_button(self, interaction: Interaction, button: Button):
        self.page += 1
        pages = self.manager.get_page(interaction.guild_id, self.page)
        
        if len(pages) == 0:
            self.page -= 1
            await interaction.response.defer()
            return
        
        await interaction.response.edit_message(content=self.format_queue(pages))
    
    @classmethod
    def format_queue(cls, page):
        page = '\n'.join(map(lambda item: item.text, page))
        return f'```\n{page}\n```'

    @classmethod
    async def create(cls, context: Context, manager: VoiceClientManager):
        pages = manager.get_page(context.guild.id, 0)
        message = await context.send(cls.format_queue(pages), view=cls(manager))


class VoiceClientCog(Cog, name='Voice Channel Commands'):

    def __init__(self, bot: Bot):
        self.bot = bot
        self.manager = VoiceClientManager()


    @Cog.listener()
    async def on_voice_state_update(
            self,
            member: Member,
            before: VoiceState,
            after: VoiceState
        ) -> None:

        if not member.bot:
            return
        
        if after.channel is None:
            await self.manager.delete(member.guild.id)
            return
        
        await self.manager.update(member.guild.id, member.guild.voice_client)


    @command(pass_context=True)
    async def queue(self, context: Context):
        await QueueView.create(context, self.manager)


    @group(pass_context=True, invoke_without_command=True, help='Adds some media to the queue.')
    async def play(self, context: Context, *args, **kwargs) -> None:
        ...


    @play.command(pass_context=True, help='Plays text via TTS.')
    async def tts(self, context: Context, *, text: str) -> None:
        player = TTSPlayer(
            text=text,
            context=context
        )
        await self.manager.try_push(player)


    @play.command(pass_context=True, aliases=['le'], help='Plays literotica stories via TTS.')
    async def literotica(self, context: Context, *, text: str) -> None:
        player = LiteroticaPlayer(
            text=text,
            context=context
        )
        await self.manager.try_push(player)


    @play.command(name='bruh', aliases=['david'], help='Says bruh.')
    async def bruh(self, context: Context) -> None:
        player = FilePlayer(
            text='./bruh.mp4',
            context=context
        )
        await self.manager.try_push(player)
    

    @play.command(name='youtube', aliases=['yt'], help='Plays youtube.')
    async def youtube(self, context: Context, *, text: str) -> None:
        player = YouTubePlayer(
            text=text,
            context=context
        )
        await self.manager.try_push(player)


    @command(name='kill', aliases=['leave', 'k'], help="Stops bot in voice channels.")
    async def kill(self, context: Context) -> None:
        channel = get(self.bot.voice_clients, guild=context.guild)

        if channel is None:
            return

        await self.manager.delete(context.guild.id)
        await channel.disconnect()


    @command(pass_context=True, aliases=['s'], help='Skips current media.')
    async def skip(self, context: Context) -> None:
        await self.manager.skip(context.guild.id)
