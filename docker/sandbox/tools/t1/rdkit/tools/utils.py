import io
import base64
def pil_image_to_base64(img, format="PNG"):
    """
    Converts a PIL Image object to a base64 string.

    Args:
        img: PIL Image object.
        format: Image format for saving to buffer (e.g., "PNG", "JPEG").

    Returns:
        A base64 encoded string representation of the image.
    """
    buffered = io.BytesIO()
    img.save(buffered, format=format)
    img_byte = buffered.getvalue()
    
    return img_byte