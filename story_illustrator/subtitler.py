import os
from typing import Dict
from datetime import timedelta
from srt import Subtitle, compose


class Subtitler:
    def __init__(self, output_directory):
        self.output_directory = output_directory

    def get_token_duration(self, token, info):
        if token == info["token"]:
            return info["duration"]
        else:
            raise Exception(
                f'token not the same! {token} <subtitle> vs {info["token"]} <mapping>'
            )

    def create_srt(
        self,
        tokens,
        timestamp_mapping: Dict,
        filename: str = "subtitles.srt",
        skip_first: str = False,
    ):
        start_time = timedelta(seconds=0)
        subs = []
        for i, token in enumerate(tokens):
            token_duration = self.get_token_duration(token, timestamp_mapping[i])
            end_time = start_time + timedelta(seconds=token_duration)
            subs.append(
                Subtitle(index=i + 1, start=start_time, end=end_time, content=token)
            )
            start_time = end_time

        if skip_first:
            subs[0].content = ""

        srt_string = compose(subs)
        os.makedirs(self.output_directory, exist_ok=True)
        with open(os.path.join(self.output_directory, filename), "w") as f:
            f.write(srt_string)
