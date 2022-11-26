import os
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.audio.AudioClip import CompositeAudioClip
from moviepy.editor import concatenate_videoclips, concatenate_audioclips
from moviepy.video.VideoClip import TextClip, ImageClip
from moviepy.video.tools.subtitles import SubtitlesClip
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip


class VideoEditor():
    def __init__(self, video_output_path, illustration_directory, narration_directory, subtitle_srt, timestamp_mapping, text_font='Georgia-Regular', text_size=24, text_color='white', ):
        self.video_output_path = video_output_path
        self.illustration_directory = illustration_directory
        self.narration_directory = narration_directory
        self.subtitle_srt = subtitle_srt
        self.timestamp_mapping = timestamp_mapping
        self.text_font = text_font
        self.text_size = text_size
        self.text_color = text_color


    def get_files(self, directory, file_type):
        files = []
        for subdir in os.scandir(directory):
            for file in os.scandir(subdir):
                if file.name.split('.')[-1] == file_type:
                    files.append(os.path.join(directory, subdir.name, file.name))
                    break
        return files


    def generate_image_clip(self):
        illustrations = self.get_files(self.illustration_directory, 'png')
        image_clips = []
        for i, img in enumerate(illustrations):
            image_clips.append(ImageClip(img).set_duration(self.timestamp_mapping[str(i)]['duration']))
        return concatenate_videoclips(image_clips, method="compose")


    def generate_narration_clip(self):
        narrations = self.get_files(self.narration_directory, 'wav')
        return concatenate_audioclips([AudioFileClip(wav) for wav in narrations])
            

    def generate(self):
        text_generator = lambda txt: TextClip(txt, font=self.text_font, fontsize=self.text_size, color=self.text_color)
        sub_clip = SubtitlesClip(self.subtitle_srt, text_generator)
        image_clip = self.generate_image_clip()
        audio_clip = self.generate_narration_clip()
        final = CompositeVideoClip([image_clip, sub_clip.set_pos(('center','center'))])
        final.audio = audio_clip
        final.write_videofile(self.video_output_path if self.video_output_path.split('.')[-1]=='mp4' else os.path.join(self.video_output_path, 'video.mp4'), fps=30)


