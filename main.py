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


input_path = "input.txt"
output_directory = "outputs"
os.makedirs(output_directory, exist_ok=True)

sp = Screenplay(input_path)
# creates pngs
#Illustrator(output_directory=os.path.join(output_directory, 'illustrations')).illustrate(sp.sentences, n_samples=1)
# creates wavs
#Narrator(output_directory=os.path.join(output_directory, 'narrations')).narrate(sp.sentences)
# creates srt
timestamp_mapping = get_timestamp_mapping(os.path.join(output_directory, "narrations"))
#Subtitler(output_directory=os.path.join(output_directory, "subtitles")).create_srt(sp.sentences, timestamp_mapping)
#creates mp4
VideoEditor(
    video_output_path = output_directory,
    illustration_directory = os.path.join(output_directory, 'illustrations'),
    narration_directory = os.path.join(output_directory, 'narrations'),
    subtitle_srt= os.path.join(output_directory, 'subtitles', 'subtitles.srt'),
    timestamp_mapping = timestamp_mapping,
    text_font='Georgia-Regular',
    text_size=24,
    text_color='white'
).generate()
