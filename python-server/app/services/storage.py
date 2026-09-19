import uuid
from pathlib import Path
from app.config import get_settings

settings = get_settings()

UPLOAD_DIR = Path("static/uploads")

MIME_EXT = {
    "image/jpeg": "jpg",
    "image/jpg": "jpg",
    "image/png": "png",
    "image/webp": "webp",
    "image/gif": "gif",
}


def save_image_and_get_url(image_bytes: bytes, mime_type: str) -> str:
    """Save uploaded image to local disk and return a publicly reachable URL."""
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    ext = MIME_EXT.get(mime_type, "jpg")
    filename = f"{uuid.uuid4().hex}.{ext}"
    (UPLOAD_DIR / filename).write_bytes(image_bytes)

    return f"{settings.public_base_url.rstrip('/')}/static/uploads/{filename}"
