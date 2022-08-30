from concurrent.futures import ThreadPoolExecutor
from io import BytesIO
from TTS.utils.synthesizer import Synthesizer
from TTS.utils.manage import ModelManager
from discord.voice_client import VoiceClient
import ffmpegfix
from mute import Mute
import asyncio
import nltk.data


class TTS:

    def __init__(
            self,
            model_name='tts_models/en/ljspeech/tacotron2-DDC_ph',
            vocoder_name='vocoder_models/en/ljspeech/multiband-melgan'
            ) -> None:

        with Mute():
            manager = ModelManager()
            tts_checkpoint, tts_config_path, _ = manager.download_model(model_name)
            vocoder_checkpoint, vocoder_config, _ = manager.download_model(vocoder_name)

            self.synthesizer = Synthesizer(
                tts_checkpoint=tts_checkpoint,
                tts_config_path=tts_config_path,
                vocoder_checkpoint=vocoder_checkpoint,
                vocoder_config=vocoder_config
            )
        
        tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
        self._split = lambda text: tokenizer.tokenize(text)
        self.is_active = False


    def _tts(self, sentence: str) -> BytesIO:
        fp = BytesIO()

        with Mute():
            try:
                wavs = self.synthesizer.tts(sentence)
                self.synthesizer.save_wav(wavs, fp)
            except:
                return None
        
        return fp
    

    async def tts(self, text: str, voice_client: VoiceClient) -> None:
        self.is_active = True
        with ThreadPoolExecutor(max_workers=1) as executor:
                
            for fp in executor.map(self._tts, self._split(text), timeout=15):

                while voice_client.is_playing():
                    await asyncio.sleep(.1)
                
                if fp is None:
                    continue

                if not voice_client.is_connected():
                    break
                
                with fp:
                    voice_client.play(ffmpegfix.FFmpegPCMAudio(executable='ffmpeg',
                                                            source=fp.read(),
                                                            pipe=True))
        self.is_active = False


class TTSQueue:

    def __init__(self) -> None:
        self.queue = []
        self.tts = TTS()
        self.is_running = True

    
    async def push(self, text: str, voice_client: VoiceClient) -> None:
        self.queue.append((text, voice_client))
    

    async def run(self) -> None:
        while self.is_running:
            if self.tts.is_active:
                await asyncio.sleep(.1)
                continue

            try:
                text, voice_client = self.queue.pop()
            except IndexError:
                await asyncio.sleep(.1)
                continue

            await self.tts.tts(text, voice_client)
    

    async def stop(self) -> None:
        self.is_running = False
