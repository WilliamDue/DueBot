from typing import Tuple
from urllib.request import urlopen, HTTPError
from discord.voice_client import VoiceClient
from bs4 import BeautifulSoup
from .tts_player import TTSPlayer
from .item import Item

class LiteroticaPlayer(TTSPlayer):

    def __init__(self, voice_client: VoiceClient) -> None:
        super().__init__(voice_client)


    def get_literotica_text(self, link: str) -> Tuple[str, str]:
        begin0 = 'https://www.literotica.com/s/'
        begin1 = 'www.literotica.com/s/'
        link_begin0 = link[:len(begin0)]
        link_begin1 = link[:len(begin1)]
        
        if link_begin0 != begin0 and link_begin1 != begin1:
            return ''
        
        blob = ''
        n = 1
        description = 'Description Was Not Found'
        
        while True:
            try:
                fp = urlopen(link + f'?page={n}')
            except HTTPError:
                break
            
            soup = BeautifulSoup(fp.read(), 'html.parser')
            fp.close()
            s = soup.find('div', {'class': 'panel article aa_eQ'})
            
            if n == 1:
                title = soup.find('h1', {'class': 'j_bm headline j_eQ'}).get_text()
                author = soup.find('a', {'class': 'y_eU'}).get_text()
                description = f'{title} by {author}'

            
            blob += ' '.join([p.get_text() for p in s.find_all('p')]) + ' '
            
            n += 1
            
        return blob, description


    async def play(self, item: Item) -> None:
        text, description = self.get_literotica_text(item.text)
        await self.lazy_play_wait(self._tts, text)