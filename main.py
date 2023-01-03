import os
import json
from omegaconf import OmegaConf
from story_illustrator.screenplay import Screenplay
from story_illustrator.illustrator import Illustrator
from story_illustrator.narrator import Narrator
from story_illustrator.subtitler import Subtitler
from story_illustrator.video_editor import VideoEditor


def get_timestamp_mapping(directory):
    mapping = {}
    for subdir in os.scandir(directory):
        for file in os.scandir(subdir):
            if file.name == "info.json":
                with open(file.path, "r") as f:
                    mapping[int(subdir.name.split("-")[0])] = json.load(f)
                break
    return mapping


conf = OmegaConf.load("config.yaml")
text = conf["input_text_directory"]
output_directory = conf["output_directory"]
os.makedirs(output_directory, exist_ok=True)

title = conf.get("title", None)
title_image = conf.get("title_image", None)

sp = Screenplay(text=text, title=title)

# creates pngs
Illustrator(
    output_directory=os.path.join(output_directory, "illustrations"),
    width=conf["image_width"],
    height=conf["image_height"],
    sentences=sp.sentences,
    n_samples=int(conf.get("num_alternative_images", 0)) + 1,
    character_descriptions=conf.get("character_descriptions", None),
    style_prompt=conf.get("image_style_prompt", ""),
    negative_prompt=conf.get("image_negative_prompt", None),
    ckpt=conf.get("stable_diffusion_model", None),
).illustrate()

# # creates wavs
# Narrator(output_directory=os.path.join(output_directory, "narrations")).narrate(
#     sp.sentences, voice='jackson'
# )

# # creates srt
# timestamp_mapping = get_timestamp_mapping(os.path.join(output_directory, "narrations"))
# Subtitler(output_directory=os.path.join(output_directory, "subtitles")).create_srt(
#     sp.sentences, timestamp_mapping.copy(), skip_first=True if title_image else False
# )

# # creates mp4
# VideoEditor(
#     video_output_path=output_directory,
#     illustration_directory=os.path.join(output_directory, "illustrations"),
#     narration_directory=os.path.join(output_directory, "narrations"),
#     subtitle_srt=os.path.join(output_directory, "subtitles", "subtitles.srt"),
#     timestamp_mapping=timestamp_mapping,
#     title_image=title_image,
#     text_font="Consolas-Bold",
#     text_size=40,
#     text_color="white",
#     text_stroke_width=2,
#     speed = 1.05
# ).generate()
