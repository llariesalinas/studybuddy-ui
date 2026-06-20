"""Image processing helpers for uploaded media.

Studybuddy serves media from local filesystem storage, so unlike a CDN-backed
service (e.g. Supabase, which transforms images on the fly) we compress images
at upload time. ``compress_image`` resizes to a bounded box, strips EXIF, and
re-encodes to WebP to keep stored avatars small.
"""

import io
import os

from PIL import Image, ImageOps
from django.core.files.base import ContentFile

# Avatars never need to be larger than this on screen; bound the longest side.
AVATAR_MAX_SIZE = (512, 512)
# WebP quality: 80 is visually near-lossless for photos at a fraction of the size.
AVATAR_QUALITY = 80


def compress_image(uploaded_file, max_size=AVATAR_MAX_SIZE, quality=AVATAR_QUALITY):
    """Resize, strip metadata, and re-encode an uploaded image to WebP.

    Args:
        uploaded_file: A Django ``UploadedFile`` (or any file-like image).
        max_size: ``(width, height)`` bounding box; aspect ratio is preserved
            and the image is never upscaled.
        quality: WebP encoder quality (1-100).

    Returns:
        A ``ContentFile`` containing WebP bytes, named ``<stem>.webp``.

    Raises:
        OSError / PIL exceptions if the file cannot be read as an image. Callers
        should treat any exception as an invalid upload.
    """
    image = Image.open(uploaded_file)

    # Honor camera orientation (EXIF) before discarding metadata, then flatten
    # transparency/palette modes onto white so WebP encoding is consistent.
    image = ImageOps.exif_transpose(image)
    if image.mode in ('RGBA', 'LA', 'P'):
        background = Image.new('RGB', image.size, (255, 255, 255))
        converted = image.convert('RGBA')
        background.paste(converted, mask=converted.split()[-1])
        image = background
    elif image.mode != 'RGB':
        image = image.convert('RGB')

    # thumbnail() preserves aspect ratio and only ever shrinks.
    image.thumbnail(max_size)

    buffer = io.BytesIO()
    image.save(buffer, format='WEBP', quality=quality)
    buffer.seek(0)

    original_name = getattr(uploaded_file, 'name', 'image') or 'image'
    stem = os.path.splitext(os.path.basename(original_name))[0] or 'image'

    return ContentFile(buffer.read(), name=f'{stem}.webp')
