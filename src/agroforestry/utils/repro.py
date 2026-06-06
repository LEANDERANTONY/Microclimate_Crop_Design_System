"""Reproducibility helpers."""
import os
import random

import numpy as np


def set_seed(seed: int = 0) -> None:
    """Seed Python and NumPy RNGs for reproducible runs."""
    os.environ["PYTHONHASHSEED"] = str(seed)
    random.seed(seed)
    np.random.seed(seed)
