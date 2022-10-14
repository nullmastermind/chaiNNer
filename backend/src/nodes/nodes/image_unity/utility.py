import os.path

import cv2
import numpy as np

from ...utils.utils import get_temp_file


def np_image_to_path(img: np.ndarray):
    save_to = get_temp_file("png")
    img = (np.clip(img, 0, 1) * 255).round().astype("uint8")
    cv2.imwrite(save_to, img)
    return save_to


def get_bin(tool_name):
    if not ("UNITY_TOOLS" in os.environ and os.path.exists(os.environ["UNITY_TOOLS"])):
        raise Exception("can not find UNITY_TOOLS in the system path")

    return os.path.join(os.environ["UNITY_TOOLS"], tool_name)
