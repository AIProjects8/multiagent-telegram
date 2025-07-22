import base64
import mimetypes

def encode_image_to_data_url(image_path: str) -> str:
    mime_type, _ = mimetypes.guess_type(image_path)
    if mime_type is None:
        raise ValueError("Could not determine the MIME type.")
    with open(image_path, "rb") as image_file:
        base64_data = base64.b64encode(image_file.read()).decode('utf-8')
    return f"data:{mime_type};base64,{base64_data}"