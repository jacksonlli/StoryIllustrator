import os
import time
import json
import torchaudio
import scipy.io.wavfile as wav

from tortoise.api import TextToSpeech
from tortoise.utils.audio import load_voice


class Narrator:
    def __init__(self, output_directory, voice="jackson", quality="fast"):
        """
        Args:
            voice: see folder in tortoise for options
            quality: "ultra_fast", "fast" (default), "standard", "high_quality"
        """

        self.output_directory = output_directory
        self.voice = voice
        self.quality = quality
        self.tts = TextToSpeech()

    def narrate(self, tokens, voice=None, selection_range=None):
        if not voice:
            voice = self.voice

        voice_samples, conditioning_latents = load_voice(voice)

        for i, token in enumerate(tokens):
            if selection_range and i not in selection_range:
                continue
            start_time = time.time()
            out_subdir = os.path.join(
                self.output_directory, "-".join([str(i), token[:150].replace('"', "").replace('.', "")])
            )
            os.makedirs(out_subdir, exist_ok=True)
            print(f"Narrating: {i+1}/{len(tokens)}-----------------------")
            gen = self.tts.tts_with_preset(
                token,
                voice_samples=voice_samples,
                conditioning_latents=conditioning_latents,
                preset=self.quality,
            )
            wav_file_path = os.path.join(
                out_subdir, f"{voice}.wav".replace('"', "").replace('.', "")
            ).replace('"', "")
            torchaudio.save(wav_file_path, gen.squeeze(0).cpu(), 24000)
            (source_rate, source_sig) = wav.read(wav_file_path)
            duration_seconds = len(source_sig) / float(source_rate)
            with open(os.path.join(out_subdir, "info.json"), "w") as outfile:
                json.dump(
                    {
                        "token": token,
                        # 'prompt': prompt,
                        "voice": voice,
                        "quality": self.quality,
                        "duration": duration_seconds,
                        "generation_time": time.time() - start_time,
                    },
                    outfile,
                )
