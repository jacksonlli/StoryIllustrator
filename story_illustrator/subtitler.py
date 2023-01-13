import os, re
from typing import Dict
from datetime import timedelta
from srt import Subtitle, compose


class Subtitler:
    def __init__(
        self,
        output_directory,
        tokens,
        timestamp_mapping: Dict,
        filename: str = "subtitles.srt",
        skip_first: str = False,
    ):
        self.output_directory = output_directory
        self.tokens = tokens
        self.timestamp_mapping = timestamp_mapping
        self.filename = filename
        self.skip_first = skip_first

    def get_token_duration(self, token, info):
        if token == info["token"]:
            return info["duration"]
        else:
            raise Exception(
                f'token not the same! {token} <subtitle> vs {info["token"]} <mapping>'
            )

    def create_srt(
        self,
    ):
        start_time = timedelta(seconds=0)
        subs = []
        for i, token in enumerate(self.tokens):
            if i not in self.timestamp_mapping:
                break
            token_duration = self.get_token_duration(token, self.timestamp_mapping[i])
            end_time = start_time + timedelta(seconds=token_duration)
            subs.append(
                Subtitle(index=i + 1, start=start_time, end=end_time, content=re.sub(r'\[.*?\]\W?', "", token))
            )
            start_time = end_time

        if self.skip_first:
            subs[0].content = ""

        srt_string = compose(subs)
        os.makedirs(self.output_directory, exist_ok=True)
        with open(os.path.join(self.output_directory, self.filename), "w") as f:
            f.write(srt_string)
