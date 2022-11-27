import os
import time
import json

from stable_diffusion.optimizedSD.optimized_txt2img import main as txt2img


class Illustrator:
    def __init__(self, output_directory, height=512, width=512, illustration_kwargs={}):
        self.output_directory = output_directory
        # recommended sizes: 384x704, 448x576, 512x512, 576x448, 704x384,
        self.height = height
        self.width = width
        self.illustration_kwargs = illustration_kwargs
        os.makedirs(output_directory, exist_ok=True)

    def illustrate(self, sentences, n_samples=1, selection_range=None):
        if "negative_prompt" not in self.illustration_kwargs:
            negative_prompt = "duplicate, morbid, mutilated, out of frame, extra fingers, mutated hand, mutation, deformed, blurry, bad anatomy, bad proportions, extra limbs, cloned face, disfigured, extra limbs, bad anatomy, gross proportions, malformed limbs, missing arms, missing legs, extra arms, extra legs, mutated hands, fused fingers, too many fingers"
        else:
            negative_prompt = self.illustration_kwargs.pop("negative_prompt")
        tokens = sentences
        for i, token in enumerate(tokens):
            if selection_range and i not in selection_range:
                continue
            start_time = time.time()
            out_subdir = os.path.join(
                self.output_directory,
                "-".join([str(i), token[:150].replace('"', "").replace(".", "")]),
            )
            prompt = (
                token
                + ", highly detailed digital artwork, intricate, trending on artstation, by WLOP and Charlie Bowater and Greg Rutkowski and Alphonse Mucha, 100mm"
            )
            print(f"Illustrating: {i+1}/{len(tokens)}-----------------------")
            txt2img(
                prompt=prompt,
                negative_prompt=negative_prompt,
                outdir=out_subdir,
                n_samples=n_samples,
                H=self.height,
                W=self.width,
                **self.illustration_kwargs,
            )
            info_dict = {
                "token": token,
                "prompt": prompt,
                "negative_prompt": negative_prompt,
            }
            info_dict.update(**self.illustration_kwargs)
            info_dict.update({"generation_time": time.time() - start_time})
            with open(
                os.path.join(out_subdir, "info.json"), "w", encoding="utf-8"
            ) as outfile:
                json.dump(info_dict, outfile)
