from __future__ import annotations

import subprocess

import numpy as np

from . import category as ImageUnityCategory
from .utility import get_bin
from ..image.load_image import ImReadNode
from ...node_base import NodeBase
from ...node_factory import NodeFactory
from ...properties.inputs import (
    TextInput,
    NumberInput,
)
from ...properties.outputs import ImageOutput
from ...utils.utils import safe_remove_file, get_temp_file


@NodeFactory.register("chainner:image:export_svg")
class ScaleXNode(NodeBase):
    def __init__(self):
        super().__init__()
        self.description = "SVG to image."
        self.inputs = [
            TextInput("SVG Path"),
            NumberInput(
                "Scale Factor",
                precision=1,
                controls_step=0.1,
                default=1.5,
                minimum=0,
                unit="x",
            ),
        ]
        self.outputs = [ImageOutput()]
        self.category = ImageUnityCategory
        self.name = "Export SVG"
        self.icon = "MdSportsEsports"

    def run(self, svg_path: str, scale_multiple: float) -> np.ndarray:
        with open(svg_path, "r") as f:
            content = f.read()
            width = int(content.split('width="')[1].split('"')[0])
            height = int(content.split('height="')[1].split('"')[0])
            save_to = get_temp_file("png")
            scale = int(8 * scale_multiple)
            subprocess.call(
                [
                    get_bin("resvg.exe"),
                    "-w",
                    "{}".format(width * scale),
                    "-h",
                    "{}".format(height * scale),
                    svg_path,
                    save_to,
                ]
            )
            subprocess.call(
                [
                    get_bin("ImageMagick-7.1.0-portable-Q8-x64/magick.exe"),
                    "mogrify",
                    "-resize",
                    "{}x{}".format(
                        int(width * scale_multiple),
                        int(height * scale_multiple),
                    ),
                    "-sharpen",
                    "0x1.0",
                    save_to,
                ]
            )
            read_node = ImReadNode()
            img, _, _ = read_node.run(save_to)

            safe_remove_file(save_to)

        return img
