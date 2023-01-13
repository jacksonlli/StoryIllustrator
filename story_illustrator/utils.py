import os
import math

def create_subdir_name(token, output_directory, i, len_tokens):
    subdir_name = edit_file_folder_name(token)
    out_subdir = os.path.join(
        output_directory,
        "-".join([str(i).zfill(int(math.log10(len_tokens) + 1)), subdir_name]),
    )
    return out_subdir

def edit_file_folder_name(name):
    invalid_chars = ["<", ">", ":", '"', "/", "\\", "|", "?", "*", "\n", ".", "’"]
    name = name[:100]
    for ch in invalid_chars:
        name = name.replace(ch, "")
    if name[-1] == ' ':
        name = name[:-1]
    return name
