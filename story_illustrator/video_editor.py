import os
import re
import json
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.audio.AudioClip import CompositeAudioClip
from moviepy.editor import concatenate_videoclips, concatenate_audioclips, vfx
from moviepy.video.VideoClip import TextClip, ImageClip
from moviepy.video.tools.subtitles import SubtitlesClip
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.audio.fx.all import volumex

from story_illustrator.utils import edit_file_folder_name


class VideoEditor:
    def __init__(
        self,
        video_output_path,
        illustration_directory,
        narration_directory,
        timestamp_mapping,
        subtitle_srt=None,
        title_image=None,
        text_font="Georgia-Regular",
        text_size=24,
        text_color="white",
        text_stroke_width=3,
        text_stroke_color="black",
        speed=1.0,
        volume_boost = 1.0,
        title = "video"
    ):
        self.video_output_path = video_output_path
        self.illustration_directory = illustration_directory
        self.narration_directory = narration_directory
        self.subtitle_srt = subtitle_srt
        self.timestamp_mapping = timestamp_mapping
        self.title_image = title_image
        self.text_font = text_font
        self.text_size = text_size
        self.text_color = text_color
        self.text_stroke_width = text_stroke_width
        self.text_stroke_color = text_stroke_color
        self.speed = speed
        self.volume_boost = volume_boost
        self.title = edit_file_folder_name(re.sub(r'\[.*?\]\W?', "", title))

    def get_files(self, directory, file_type):
        files = []
        for subdir in os.scandir(directory):
            for file in os.scandir(subdir):
                if file.name.split(".")[-1] == file_type:
                    files.append(os.path.join(directory, subdir.name, file.name))
                    break
        return files

    def generate_image_clip(self):
        illustrations = self.get_files(self.illustration_directory, "png")
        image_clips = []
        for i, img in zip(self.timestamp_mapping, illustrations):
            image_clips.append(
                ImageClip(img).set_duration(self.timestamp_mapping[i]["duration"])
            )
        if self.title_image:
            margin = 20
            title_image_clip = ImageClip(self.title_image)
            if title_image_clip.w > image_clips[0].w - 2 * margin:
                title_image_clip = title_image_clip.resize(
                    (image_clips[0].w - 2 * margin) / title_image_clip.w
                )
            image_clips[0] = CompositeVideoClip(
                [image_clips[0], title_image_clip.set_pos(("center", "center"))]
            ).set_duration(image_clips[0].duration)
        return concatenate_videoclips(image_clips, method="compose")

    def generate_narration_clip(self):
        narrations = self.get_files(self.narration_directory, "wav")
        narration_clip = concatenate_audioclips(
            [AudioFileClip(wav) for wav in narrations]
        )
        return volumex(narration_clip, self.volume_boost)

    def generate(self):
        vid = self.generate_image_clip()
        
        if self.subtitle_srt:
            text_generator = lambda txt: TextClip(
                txt,
                font=self.text_font,
                fontsize=self.text_size,
                color=self.text_color,
                stroke_width=self.text_stroke_width,
                stroke_color=self.text_stroke_color,
                size = vid.size,
                method='caption',
                align='north'
            )
            sub_clip = SubtitlesClip(self.subtitle_srt, text_generator)
            vid = CompositeVideoClip([vid, sub_clip.set_position(('center', 0.8), relative=True)])
        audio_clip = self.generate_narration_clip()
        vid.audio = audio_clip
        vid = vid.fx(vfx.speedx, self.speed)
        vid.write_videofile(
            self.video_output_path
            if self.video_output_path.split(".")[-1] == "mp4"
            else os.path.join(self.video_output_path, f"{self.title}.mp4"),
            fps=30,
        )
