import os
import json
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
                    mapping[subdir.name.split("-")[0]] = json.load(f)
                break
    return mapping


input_directory = "inputs"
output_directory = "outputs"
os.makedirs(output_directory, exist_ok=True)

text = os.path.join(input_directory, "text.txt")
title = (
    os.path.join(input_directory, "title.txt")
    if os.path.isfile(os.path.join(input_directory, "title.txt"))
    else None
)
title_image = (
    os.path.join(input_directory, "title.png")
    if os.path.isfile(os.path.join(input_directory, "title.png"))
    else None
)

sp = Screenplay(text=text, title=title)
# creates pngs
# Illustrator(
#     output_directory=os.path.join(output_directory, "illustrations"),
#     width=384,
#     height=704,
# ).illustrate(sp.sentences, n_samples=1)
# creates wavs
# Narrator(output_directory=os.path.join(output_directory, "narrations")).narrate(
#     sp.sentences
# )
# creates srt
timestamp_mapping = get_timestamp_mapping(os.path.join(output_directory, "narrations"))
# Subtitler(output_directory=os.path.join(output_directory, "subtitles")).create_srt(
#     sp.sentences, timestamp_mapping.copy(), skip_first=True if title_image else False
# )
# creates mp4
VideoEditor(
    video_output_path=output_directory,
    illustration_directory=os.path.join(output_directory, "illustrations"),
    narration_directory=os.path.join(output_directory, "narrations"),
    subtitle_srt=os.path.join(output_directory, "subtitles", "subtitles.srt"),
    timestamp_mapping=timestamp_mapping,
    title_image = title_image,
    text_font="Consolas-Bold",
    text_size=40,
    text_color="white",
    text_stroke_width=2,
).generate()
