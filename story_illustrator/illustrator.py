import os
import math
import time
import json
import re
from typing import List, Union
from nltk.tokenize import sent_tokenize, word_tokenize
import spacy
from pattern.en import conjugate

# from stable_diffusion.optimizedSD.optimized_txt2img import main as txt2img
from stable_diffusion.scripts.txt2img import main as txt2img


class Illustrator:
    def __init__(
        self,
        output_directory,
        sentences,
        height=512,
        width=512,
        illustration_kwargs={},
        character_descriptions={},
        n_samples=1,
        selection_range=None,
        remove_dialogue=True,
        tokenization_length=20,
        style_prompt="highly detailed digital artwork, intricate, trending on artstation, by WLOP and Greg Rutkowski and Alphonse Mucha, 100mm",
        negative_prompt="duplicate, morbid, mutilated, out of frame, extra fingers, mutated hand, mutation, deformed, blurry, bad anatomy, bad proportions, extra limbs, cloned face, disfigured, extra limbs, bad anatomy, gross proportions, malformed limbs, missing arms, missing legs, extra arms, extra legs, mutated hands, fused fingers, too many fingers",
        prefix_prompt="photo of the most beautiful artwork in the world featuring ",
        ckpt=None,
        real_ersgan_executable_path=None,
        gfpgan_model=None,
    ):
        self.output_directory = output_directory
        self.sentences = sentences
        # recommended sizes: 384x704, 448x576, 512x512, 576x448, 704x384,
        self.height = height
        self.width = width
        self.illustration_kwargs = illustration_kwargs
        self.character_descriptions = character_descriptions
        self.n_samples = n_samples
        self.selection_range = selection_range
        self.remove_dialogue = remove_dialogue
        self.tokenization_length = tokenization_length
        self.style_prompt = style_prompt
        self.negative_prompt = negative_prompt
        self.prefix_prompt = prefix_prompt
        self.ckpt = ckpt
        self.real_ersgan_executable_path=real_ersgan_executable_path
        self.gfpgan_model = gfpgan_model
        self.nlp = spacy.load("en_core_web_sm")
        os.makedirs(output_directory, exist_ok=True)

    def illustrate(self):
        # tokens = self._tokenize()
        tokens = self.sentences
        for i, token in enumerate(tokens):
            if self.selection_range and i not in self.selection_range:
                continue
            start_time = time.time()
            invalid_chars = ["<", ">", ":", '"', "/", "\\", "|", "?", "*", "\n", ".", "’"]
            subdir_name = token[:150]
            for ch in invalid_chars:
                subdir_name = subdir_name.replace(ch, "")

            out_subdir = os.path.join(
                self.output_directory,
                "-".join([str(i).zfill(int(math.log10(len(tokens)) + 1)), subdir_name]),
            )

            prompt = self._prompt_engineering(token)
            print(f"Illustrating: {i+1}/{len(tokens)}-----------------------")
            txt2img(
                prompt=prompt,
                negative_prompt=self.negative_prompt,
                outdir=out_subdir,
                n_samples=self.n_samples,
                H=self.height,
                W=self.width,
                optimize=False,
                ckpt=self.ckpt,
                real_ersgan_executable_path=self.real_ersgan_executable_path,
                gfpgan_model=self.gfpgan_model,
                only_keep_final=True,
                **self.illustration_kwargs,
            )

            info_dict = {
                "token": token,
                "prompt": prompt,
                "negative_prompt": self.negative_prompt,
            }
            info_dict.update(**self.illustration_kwargs)
            info_dict.update({"generation_time": time.time() - start_time})
            with open(
                os.path.join(out_subdir, "info.json"), "w", encoding="utf-8"
            ) as outfile:
                json.dump(info_dict, outfile)


    def _split_sentence(self, token):
        doc = self.nlp(token)
        if len(doc) >= self.tokenization_length:
            subject_found = False
            split_indexes = []
            split_candidate = None
            for i, sub_tok in enumerate(doc):
                if sub_tok.dep_ in ["punct"]:  # "cc", 
                    split_candidate = i
                elif sub_tok.dep_ == "nsubj":
                    if subject_found and split_candidate:
                        # split by punct, or cc
                        split_indexes.append(split_candidate)
                    subject_found = True
            split_indexes.append(len(token))
            splits = []
            for i in range(len(split_indexes)):
                splits.append(
                    doc[(split_indexes[i - 1] if i > 0 else -1) + 1 : split_indexes[i]]
                )
        else:
            splits = [token]
        return splits

    def _tokenize(self):
        """
        Split sentences into sub sentences when possible
        """
        if isinstance(self.sentences, str):
            self.tokens = sent_tokenize(self.sentences)
        else:
            self.tokens = self.sentences
        new_tokens = []
        for token in self.tokens:
            new_tokens += self._split_sentence(token)
        self.tokens = new_tokens
        return self.tokens

    def _get_gender(self, token):
        male_identifiers = {"strong": ["he"], "soft": ["him", "his"]}
        female_identifiers = {"strong": ["she"], "soft": ["her"]}

        gender = ""
        for word in word_tokenize(token):
            word = word.lower()
            if word in male_identifiers["strong"]:
                gender = "male"
                break
            elif word in female_identifiers["strong"]:
                gender = "female"
                break
            elif gender == "" and word in male_identifiers["soft"]:
                gender = "male"
            elif gender == "" and word in female_identifiers["soft"]:
                gender = "female"
        return gender

    def _key_word_redudancy(self, token):
        doc = self.nlp(token)
        key_words = []
        for sub_tok in doc:
            if sub_tok.pos_ in ["PROPN", "NOUN"]:
                key_words.append(sub_tok.text)
            elif sub_tok.pos_ == "VERB":
                base_verb = sub_tok.lemma_
                for i in range(2):
                    try:
                        conjugated_verb = conjugate(base_verb, "part")
                        break
                    except Exception:
                        conjugated_verb = base_verb
                key_words.append(conjugated_verb)
        return " ".join(key_words)

    def replace_characters_by_description(self, token):
        for character, descr in self.character_descriptions.items():
            token = token.replace(character, descr)
        return token

    def _prompt_engineering(self, token):
        # remove dialogue
        if self.remove_dialogue:
            token = re.sub('"[^"]*?[!.?]"', "", token)
        token = self.replace_characters_by_description(token)
        # add style
        return (
            self.prefix_prompt
            + " "
            + self._get_gender(token)
            + ", "
            + self._key_word_redudancy(token)
            + ", "
            + token
            + ", "
            + self.style_prompt
        )
