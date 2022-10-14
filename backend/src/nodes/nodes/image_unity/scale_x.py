from __future__ import annotations

import subprocess

import numpy as np

from . import category as ImageUnityCategory
from .utility import np_image_to_path, get_bin
from ..image.load_image import ImReadNode
from ...node_base import NodeBase
from ...node_factory import NodeFactory
from ...properties import expression
from ...properties.inputs import ImageInput, NumberInput
from ...properties.outputs import ImageOutput
from ...utils.utils import safe_remove_file


@NodeFactory.register("chainner:image:scalex")
class ScaleXNode(NodeBase):
    def __init__(self):
        super().__init__()
        self.description = "Use scalex to scale an image."
        self.inputs = [
            ImageInput(),
            NumberInput(
                "Scale Factor W",
                precision=0,
                controls_step=1,
                default=2,
                maximum=4,
                minimum=1,
            ),
            NumberInput(
                "Scale Factor H",
                precision=0,
                controls_step=1,
                default=2,
                maximum=4,
                minimum=1,
            ),
        ]
        self.outputs = [
            ImageOutput(
                image_type=expression.Image(
                    width="max(1, int & round(Input0.width * Input1))",
                    height="max(1, int & round(Input0.height * Input2))",
                    channels_as="Input0",
                )
            )
        ]
        self.category = ImageUnityCategory
        self.name = "Scale X"
        self.icon = "MdSportsEsports"

    def run(
        self,
        img: np.ndarray,
        amount_w: float,
        amount_h: float,
    ) -> np.ndarray:
        input_path = np_image_to_path(img)
        subprocess.run(
            [
                get_bin("scale2x-4.0-windows-x86/scalex.exe"),
                "-k",
                "{}x{}".format(amount_w, amount_h),
                input_path,
                input_path,
            ]
        )
        read_node = ImReadNode()
        img, _, _ = read_node.run(input_path)

        safe_remove_file(input_path)

        return img
