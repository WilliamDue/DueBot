from TTS.utils.synthesizer import Synthesizer
from TTS.utils.manage import ModelManager
from discord.voice_client import VoiceClient
from io import BufferedReader, BytesIO
from mute import Mute
from .abstract_player import Player
import nltk.data
from discord.ext.commands.context import Context


class TTSPlayer(Player):

    def __init__(self, text: str, context: Context) -> None:
        super().__init__(text, context)

        model_name='tts_models/en/ljspeech/tacotron2-DDC_ph'
        vocoder_name='vocoder_models/en/ljspeech/multiband-melgan'
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


    def _tts(self, sentence: str) -> BytesIO:
        fp = BytesIO()

        with Mute():
            try:
                wavs = self.synthesizer.tts(sentence)
                self.synthesizer.save_wav(wavs, fp)
            except:
                return None
        
        return fp


    async def play(self, voice_client: VoiceClient) -> None:
        await self.lazy_play_wait(voice_client, self._tts, [self.text])