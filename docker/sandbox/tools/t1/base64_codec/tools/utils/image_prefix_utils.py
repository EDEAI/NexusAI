import mimetypes
import re


def wrap_mime_text_with_prefix(mime_text: str) -> str:
    return f"data:{mime_text};base64,"


def extract_mime_type(data_uri: str) -> str | None:
    match = re.search(r"data:image/([\w\-+]+);base64", data_uri)
    if not match:
        return None

    mime_subtype = match.group(1)
    full_mime = f"image/{mime_subtype}"

    if mimetypes.guess_extension(full_mime):
        return full_mime
    else:
        return None
