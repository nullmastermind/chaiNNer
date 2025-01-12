from __future__ import annotations

from enum import Enum

import numpy as np

from ...impl.fill_alpha import (
    convert_to_binary_alpha,
    fill_alpha_edge_extend,
    fill_alpha_fragment_blur,
)
from ...node_base import NodeBase
from ...node_factory import NodeFactory
from ...properties import expression
from ...properties.inputs import EnumInput, ImageInput
from ...properties.outputs import ImageOutput
from . import category as ImageChannelCategory


class AlphaFillMethod(Enum):
    EXTEND_TEXTURE = 1
    EXTEND_COLOR = 2


@NodeFactory.register("chainner:image:fill_alpha")
class FillAlphaNode(NodeBase):
    def __init__(self):
        super().__init__()
        self.description = (
            "Fills the transparent pixels of an image with nearby colors."
        )
        self.inputs = [
            ImageInput("RGBA", channels=4),
            EnumInput(AlphaFillMethod, label="Fill Method"),
        ]
        self.outputs = [
            ImageOutput(
                "RGB",
                image_type=expression.Image(size_as="Input0"),
                channels=3,
            ),
        ]
        self.category = ImageChannelCategory
        self.name = "Fill Alpha"
        self.icon = "MdOutlineFormatColorFill"
        self.sub = "Miscellaneous"

    def run(self, img: np.ndarray, method: AlphaFillMethod) -> np.ndarray:
        """Fills transparent holes in the given image"""

        if method == AlphaFillMethod.EXTEND_TEXTURE:
            # Preprocess to convert the image into binary alpha
            convert_to_binary_alpha(img)
            img = fill_alpha_fragment_blur(img)

            convert_to_binary_alpha(img)
            img = fill_alpha_edge_extend(img, 8)
        elif method == AlphaFillMethod.EXTEND_COLOR:
            convert_to_binary_alpha(img)
            img = fill_alpha_edge_extend(img, 40)
        else:
            assert False, f"Invalid alpha fill method {method}"

        # Finally, add a black background and convert to RGB
        img[:, :, 0] *= img[:, :, 3]
        img[:, :, 1] *= img[:, :, 3]
        img[:, :, 2] *= img[:, :, 3]
        return img[:, :, :3]
