"""Storage backend selection for uploaded product media (images and videos).

Each `select_*_storage` function is referenced by import path as the `storage=`
callable on the relevant FileField, so it is never baked into migrations as a
concrete object. Returns the appropriate Cloudinary storage when credentials are
present, falls back to the local filesystem otherwise.
"""
import os

from django.core.files.storage import FileSystemStorage


def cloudinary_enabled():
    return bool(
        os.environ.get('CLOUDINARY_URL')
        or os.environ.get('CLOUDINARY_CLOUD_NAME')
    )


def select_image_storage():
    if cloudinary_enabled():
        try:
            from cloudinary_storage.storage import MediaCloudinaryStorage
            return MediaCloudinaryStorage()
        except Exception:
            pass
    return FileSystemStorage()


def select_video_storage():
    if cloudinary_enabled():
        try:
            from cloudinary_storage.storage import VideoMediaCloudinaryStorage
            return VideoMediaCloudinaryStorage()
        except Exception:
            # Misconfigured/unavailable Cloudinary must not break model loading.
            pass
    return FileSystemStorage()
