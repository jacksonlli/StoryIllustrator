import os
import time
import json
import math
import torchaudio
import numpy as np
import scipy.io.wavfile as wav

from tortoise.api import TextToSpeech
from tortoise.utils.audio import load_voice

from story_illustrator.utils import create_subdir_name


class Narrator:
    def __init__(
        self,
        output_directory,
        tokens,
        voice="jackson",
        quality="fast",
        silence=0,
        selection_range=None,
    ):
        """
        Args:
            voice: see folder in tortoise for options
            quality: "ultra_fast", "fast" (default), "standard", "high_quality"
        """

        self.output_directory = output_directory
        self.tokens = tokens
        self.voice = voice
        self.quality = quality
        self.silence = float(silence)
        self.selection_range = selection_range
        self.tts = TextToSpeech()

    def process_token(self, token):
        token = token.replace("[WP]", "Writing prompt")
        token = token.replace("(", "[")
        token = token.replace(")", "]")
        token = token.replace("] ", "]")
        return token
    
    def pad_audio(self, data, fs, T):
        """
        Args:
            data: source_sig
            fs: source_rate
            T: silence to append in seconds
        """
        # Create the target shape 
        shape = data.shape
        # Calculate number of zero samples to append
        N_pad = int(fs * T)
        shape = (N_pad,) + shape[1:]
        # Stack only if there is something to append    
        if shape[0] > 0:                
            if len(shape) > 1:
                return np.vstack((data, np.zeros(shape, data.dtype)))
            else:
                return np.hstack((data, np.zeros(shape, data.dtype)))
        else:
            return data

    def narrate(self):

        voice_samples, conditioning_latents = load_voice(self.voice)

        for i, token in enumerate(self.tokens):
            if self.selection_range and i not in self.selection_range:
                continue
            start_time = time.time()
            out_subdir = create_subdir_name(token, self.output_directory, i, len(self.tokens))
            os.makedirs(out_subdir, exist_ok=True)
            print(f"Narrating: {i}/{len(self.tokens)}-----------------------")
            gen = self.tts.tts_with_preset(
                self.process_token(token),
                voice_samples=voice_samples,
                conditioning_latents=conditioning_latents,
                preset=self.quality,
            )
            wav_file_path = os.path.join(out_subdir, f"{self.voice}.wav").replace('"', "")
            torchaudio.save(wav_file_path, gen.squeeze(0).cpu(), 24000)
            (source_rate, source_sig) = wav.read(wav_file_path)
            out_data = self.pad_audio(data=source_sig, fs=source_rate, T=self.silence)
            m = np.max(np.abs(out_data))
            sigf32 = (out_data/m).astype(np.float32)
            wav.write(wav_file_path, int(source_rate), sigf32)
            duration_seconds = len(out_data) / float(int(source_rate))
            with open(
                os.path.join(out_subdir, "info.json"), "w", encoding="utf-8"
            ) as outfile:
                json.dump(
                    {
                        "token": token,
                        # 'prompt': prompt,
                        "voice": self.voice,
                        "quality": self.quality,
                        "duration": duration_seconds,
                        "generation_time": time.time() - start_time,
                    },
                    outfile,
                )
