import os.path
import shutil
import tempfile
import uuid
from pathlib import Path

import numpy as np
import cv2


def get_temp_dir():
    temp_dir = os.path.join(tempfile.gettempdir(), "chaiNNer/unity")
    Path(temp_dir).mkdir(parents=True, exist_ok=True)
    return temp_dir


def get_temp_file(ext: str):
    return "{}".format(
        os.path.join(get_temp_dir(), "{}.{}".format(uuid.uuid4().hex, ext))
    ).replace("\\", "/")


def np_image_to_path(img: np.ndarray):
    save_to = get_temp_file("png")
    img = (np.clip(img, 0, 1) * 255).round().astype("uint8")
    cv2.imwrite(save_to, img)
    return save_to


def get_bin(tool_name):
    if not ("UNITY_TOOLS" in os.environ and os.path.exists(os.environ["UNITY_TOOLS"])):
        raise Exception("can not find UNITY_TOOLS in the system path")

    return os.path.join(os.environ["UNITY_TOOLS"], tool_name)


def clean_temp():
    folder = get_temp_dir()
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print("Failed to delete %s. Reason: %s" % (file_path, e))


def safe_remove_file(file_path):
    try:
        os.unlink(file_path)
    except Exception as e:
        print("Failed to delete %s. Reason: %s" % (file_path, e))
