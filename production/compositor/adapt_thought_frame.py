"""Adapt an existing empty painted puff to thought content; never warp the picture."""
import numpy as np
from PIL import Image
from scipy.ndimage import binary_erosion


def adapt(frame, safe_unused, size):
    """Fit a simple painted puff to a content-specific aspect ratio.

    Only the empty decorative frame is resampled independently in x/y. Its
    hand-painted outline/colour is retained. Actual thought content must use
    one independent uniform scale, original pigment strength and no clipping.
    """
    out=frame.convert('RGBA').resize(tuple(size),Image.Resampling.LANCZOS)
    safe=binary_erosion(np.asarray(out)[:,:,3]>240,iterations=8)
    return out,Image.fromarray(safe.astype(np.uint8)*255)
