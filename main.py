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

print(f"Starting-----------------------")

conf = OmegaConf.load("config.yaml")
text = conf["input_text_directory"]
output_directory = conf["output_directory"]
os.makedirs(output_directory, exist_ok=True)

title = conf.get("title", None)
title_image = conf.get("title_image", None)


sp = Screenplay(text=text, title=title)

if conf.get('illustrations', False):
    # creates pngs
    Illustrator(
        output_directory=os.path.join(output_directory, "illustrations"),
        width=conf["image_width"],
        height=conf["image_height"],
        sentences=sp.illustration_sentences,
        n_samples=int(conf.get("num_alternative_images", 0)) + 1,
        character_descriptions=conf.get("character_descriptions", None),
        style_prompt=conf.get("image_style_prompt", ""),
        negative_prompt=conf.get("image_negative_prompt", None),
        prefix_prompt=conf.get("image_prefix_prompt", None),
        ckpt=conf.get("stable_diffusion_model", None),
        illustration_kwargs=conf.get('illustration_kwargs', {
            'plms': False,
            'ddim_steps':30,
            'scale': 10,
        }),
        real_ersgan_executable_path=conf.get("real_ersgan_executable", None),
        gfpgan_model=conf.get("gfpgan_model", None),
        selection_range=list(
            range(
                conf.get("illustration_range", (0, None))[0],
                conf.get("illustration_range", (0, None))[1] if conf.get("illustration_range", (0, None))[1] else len(sp.illustration_sentences)
            )
        ),
        remove_dialogue=conf.get('illustration_remove_dialogue', False)
    ).illustrate()

if conf.get('narrations', False):
    # creates wavs
    Narrator(
        output_directory=os.path.join(output_directory, "narrations"),
        tokens=sp.narration_sentences,
        voice=conf.get('voice', 'train_dotrice'),
        selection_range=list(
            range(
                conf.get("narration_range", (0, None))[0],
                conf.get("narration_range", (0, None))[1] if conf.get("narration_range", (0, None))[1] else len(sp.narration_sentences)
            )
        ),
        silence=conf.get("narration_padding", 0)
    ).narrate()

timestamp_mapping = get_timestamp_mapping(os.path.join(output_directory, "narrations"))
# # creates srt
if conf.get('create_srt', False):
    Subtitler(
        output_directory=os.path.join(output_directory, "subtitles"),
        tokens=sp.narration_sentences,
        timestamp_mapping=timestamp_mapping.copy(),
        skip_first=True if title_image else False
    ).create_srt()

if conf.get('video', False):
    # creates mp4
    VideoEditor(
        video_output_path=output_directory,
        illustration_directory=os.path.join(output_directory, "illustrations"),
        narration_directory=os.path.join(output_directory, "narrations"),
        subtitle_srt=os.path.join(output_directory, "subtitles", "subtitles.srt") if conf.get('use_srt', False) else None,
        timestamp_mapping=timestamp_mapping,
        title_image=title_image,
        text_font="Consolas-Bold",
        text_size=60,
        text_color="white",
        text_stroke_width=3,
        speed = conf.get('speed', 1.00),
        title=title
    ).generate()
