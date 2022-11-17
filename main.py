import os
import json
from story_illustrator.screenplay import Screenplay
from story_illustrator.illustrator import Illustrator
from story_illustrator.narrator import Narrator
from story_illustrator.subtitler import Subtitler


def get_timestamp_mapping(directory):
    mapping = {}
    for subdir in os.scandir(directory):
        for file in os.scandir(subdir):
            if file.name == "info.json":
                with open(file.path, "r") as f:
                    mapping[subdir.name.split("-")[0]] = json.load(f)
    return mapping


input_path = "input.txt"
output_directory = "outputs"
sp = Screenplay(input_path)
# Illustrator(output_directory=os.path.join(output_directory, 'illustrations')).illustrate(sp.sentences, n_samples=1)
# Narrator(output_directory=os.path.join(output_directory, 'narrations')).narrate(sp.sentences, selection_range=[0])
Subtitler(output_directory=os.path.join(output_directory, "subtitles")).create_srt(
    sp.sentences, get_timestamp_mapping(os.path.join(output_directory, "narrations"))
)
