# Copyright 2022 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Modifications by Henrique Morimitsu
# - Adapt code from JAX to PyTorch

"""Mask schedule functions R."""
import math
import numpy as np


def schedule(
    ratio: float,
    total_unknown: int,
    method: str = "cosine",
    beta:float =1.0
) -> float:
    """Generates a mask rate by scheduling mask functions R.

    Given a ratio in [0, 1), we generate a masking ratio from (0, 1]. During
    training, the input ratio is uniformly sampled; during inference, the input
    ratio is based on the step number divided by the total iteration number: t/T.
    Based on experiements, we find that masking more in training helps.
    Args:
        ratio: The uniformly sampled ratio [0, 1) as input.
        total_unknown: The total number of tokens that can be masked out. For
        example, in MaskGIT, total_unknown = 256 for 256x256 images and 1024 for
        512x512 images.
        method: implemented functions are ["uniform", "cosine", "pow", "log", "exp"]
        "pow2.5" represents x^2.5

    Returns:
        The mask rate (float).
    """
    if method == "uniform":
        mask_ratio = 1. - ratio
    elif "pow" in method:
        exponent = float(method.replace("pow", ""))
        mask_ratio = 1. - ratio**exponent
    elif method == "cosine":
        mask_ratio = np.cos(math.pi / 2. * ratio)
    elif method == "log":
        mask_ratio = -np.log2(ratio) / np.log2(total_unknown.cpu())
    elif method == "exp":
        mask_ratio = 1 - np.exp2(-np.log2(total_unknown) * (1 - ratio))
    elif method == "curve":
        mask_ratio = 1- (ratio + beta*ratio*(1-ratio))
    # Clamps mask into [epsilon, 1)
    mask_ratio = np.clip(mask_ratio, 1e-6, 1.)
    return mask_ratio