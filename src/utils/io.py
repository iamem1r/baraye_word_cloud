import json
from typing import Union
from pathlib import Path


def read_json(json_path: Union[Path, str]):
    """Reads a json file and returns the dict
    """
    with open(json_path) as f:
        return json.load(f)

def read_file(file_path: Union[Path, str]):
    """Reads a file and returns the content
    """
    with open(file_path) as f:
        return f.read()