from __future__ import annotations

import os
import subprocess
import re

import cv2
import numpy as np

from . import category as ImageUnityCategory
from .utility import (
    np_image_to_path,
    get_bin,
)
from ...node_base import NodeBase
from ...node_factory import NodeFactory
from ...properties.inputs import ImageInput, NumberInput
from ...properties.outputs import TextOutput
from ...utils.utils import safe_remove_file, get_temp_dir, get_temp_file


@NodeFactory.register("chainner:image:trace_color")
class ScaleXNode(NodeBase):
    def __init__(self):
        super().__init__()
        self.description = "Trace an image."
        self.inputs = [
            ImageInput(),
            NumberInput(
                "Scans",
                precision=0,
                controls_step=1,
                default=256,
                maximum=256,
                minimum=1,
            ),
            NumberInput(
                "Smooth",
                precision=0,
                controls_step=1,
                default=0,
                maximum=1,
                minimum=0,
            ),
            NumberInput(
                "Stack",
                precision=0,
                controls_step=1,
                default=1,
                maximum=1,
                minimum=0,
            ),
            NumberInput(
                "Remove Background",
                precision=0,
                controls_step=1,
                default=1,
                maximum=1,
                minimum=0,
            ),
            NumberInput(
                "Remove White Color",
                precision=0,
                controls_step=1,
                default=1,
                maximum=1,
                minimum=0,
            ),
            NumberInput(
                "Remove Origin Image",
                precision=0,
                controls_step=1,
                default=1,
                maximum=1,
                minimum=0,
            ),
            NumberInput(
                "Speckles",
                precision=0,
                controls_step=1,
                default=1,
                maximum=256,
                minimum=0,
            ),
            NumberInput(
                "Smooth Corners",
                precision=1,
                controls_step=0.01,
                default=1.0,
                maximum=1.34,
                minimum=0,
            ),
            NumberInput(
                "Optimize",
                precision=2,
                controls_step=0.01,
                default=0.20,
                maximum=5.0,
                minimum=0,
            ),
        ]
        self.outputs = [TextOutput("SVG Path")]
        self.category = ImageUnityCategory
        self.name = "Trace Bitmap"
        self.icon = "MdSportsEsports"

    def run(
        self,
        img: np.ndarray,
        scans: float,
        is_smooth: int,
        is_stack: int,
        is_remove_background: int,
        is_remove_white_color: int,
        is_remove_origin_image: int,
        speckles: float,
        smooth_corners: float,
        optimize: float,
    ) -> str:
        input_path = np_image_to_path(img)

        if is_remove_white_color == 1:
            mat = cv2.imread(input_path, cv2.IMREAD_UNCHANGED)
            rows, cols, _ = mat.shape
            for i in range(rows):
                for j in range(cols):
                    p = mat[i, j]
                    if p[0] == 255 and p[1] == 255 and p[2] == 255 and p[3] == 255:
                        p[0] = 254
                        p[1] = 254
                        p[2] = 254
                        mat[i, j] = p
            cv2.imwrite(input_path, mat)

        options = "{},{},{},{},{},{},{}".format(
            scans,
            "true" if is_smooth != 0 else "false",
            "true" if is_stack != 0 else "false",
            "true" if is_remove_background != 0 else "false",
            speckles,
            smooth_corners,
            optimize,
        )
        svg_file = get_temp_file("svg")
        svg_filename = os.path.basename(svg_file)
        actions = "select-all;selection-trace:{};export-filename:{};export-do;".format(
            options,
            svg_filename,
        )
        subprocess.call(
            " ".join(
                [
                    get_bin("inkscape/bin/inkscape.exe"),
                    "--actions={}".format(actions),
                    input_path,
                    "--batch-process",
                ]
            ),
            cwd=get_temp_dir(),
        )

        # remove noise
        if os.path.exists(svg_file):
            f = open(svg_file, "r")
            content = f.read()
            if is_remove_origin_image == 1:
                content = re.sub(r"<image((.|\n)*?)/>", "", content)
            if is_remove_white_color == 1:
                content = re.sub(
                    r"<path((.|\n)*?)fill:#fefefe((.|\n)*?)/>",
                    "",
                    content,
                )
            with open(svg_file, "w") as f:
                f.write(content)
                f.close()
            subprocess.call([get_bin("svgcleaner-cli.exe"), svg_file, svg_file])

        safe_remove_file(input_path)

        return svg_file
