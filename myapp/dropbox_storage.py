import io
import os

from django.core.cache import cache
from django.core.files.base import ContentFile
from django.core.files.storage import Storage
from django.utils.deconstruct import deconstructible
from PIL import Image

from . import dropbox_utils

ROOT = '/Manjunath Academy/Media'
LINK_CACHE_SECONDS = 60 * 60 * 24 * 30  # shared links never expire, so cache them for a month
FAILURE_CACHE_SECONDS = 60  # don't hammer Dropbox with 2 failed calls per image on every request
EXISTS_CACHE_SECONDS = 300  # files are rarely deleted/replaced at the same path; 5 min is plenty fresh
_MISS = object()

# Extensions we re-encode to WebP on upload for smaller downloads / faster page loads. GIF is left
# alone (conversion would need special handling to keep animation) and SVG needs no help.
CONVERTIBLE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif'}
MAX_DIMENSION = 1920  # no layout on the site needs anything wider/taller than this
WEBP_QUALITY = 82


def _clean_name(name):
    # Django's upload_to/filename joining runs through os.path.join/normpath, which produces
    # backslashes on Windows dev machines. Dropbox's API only accepts forward-slash paths.
    return name.replace('\\', '/').lstrip('/')


def _to_webp_bytes(raw):
    """Re-encodes image bytes as WebP, capped to MAX_DIMENSION. Returns None if `raw` isn't a
    decodable image (caller should fall back to uploading it unchanged)."""
    try:
        img = Image.open(io.BytesIO(raw))
        img.load()
    except Exception:
        return None
    if img.mode not in ('RGB', 'RGBA'):
        img = img.convert('RGBA') if img.mode in ('P', 'LA') or 'transparency' in img.info else img.convert('RGB')
    if img.width > MAX_DIMENSION or img.height > MAX_DIMENSION:
        img.thumbnail((MAX_DIMENSION, MAX_DIMENSION), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, 'WEBP', quality=WEBP_QUALITY, method=6)
    return buf.getvalue()


@deconstructible
class DropboxStorage(Storage):
    """Stores every upload (banners, course videos, e-library PDFs, thumbnails, etc.) directly on
    Dropbox instead of the local (ephemeral, on Railway) disk. FieldFile.name stays a short relative
    path like 'courses/thumb1.jpg' — that name plus ROOT is all that's needed to resolve the Dropbox
    path, so a restored database renders working image/video URLs with no separate media restore step.

    Photos (jpg/png/etc.) are also re-encoded to WebP and capped to MAX_DIMENSION on the way in, since
    that's the single biggest lever for page-load speed when every image ships straight to the browser."""

    def get_available_name(self, name, max_length=None):
        name = _clean_name(name)
        root, ext = os.path.splitext(name)
        if ext.lower() in CONVERTIBLE_EXTENSIONS:
            name = f'{root}.webp'
        return super().get_available_name(name, max_length=max_length)

    def _full_path(self, name):
        return f'{ROOT}/{_clean_name(name)}'

    def _cache_key(self, name):
        return f'dbx_url:{_clean_name(name)}'

    def _exists_cache_key(self, name):
        return f'dbx_exists:{_clean_name(name)}'

    def _save(self, name, content):
        name = _clean_name(name)
        content.seek(0)
        raw = content.read()
        if name.lower().endswith('.webp'):
            raw = _to_webp_bytes(raw) or raw
        full_path = self._full_path(name)
        dropbox_utils.upload_bytes(full_path, raw)
        cache.set(self._exists_cache_key(name), True, EXISTS_CACHE_SECONDS)
        # Resolve the shared link now, while the admin's upload request is already in flight,
        # instead of leaving it for the first site visitor who views this file to pay for.
        try:
            cache.set(self._cache_key(name), dropbox_utils.get_direct_link(full_path), LINK_CACHE_SECONDS)
        except dropbox_utils.DropboxError:
            pass
        return name

    def _open(self, name, mode='rb'):
        return ContentFile(dropbox_utils.download_bytes(self._full_path(name)), name=name)

    def delete(self, name):
        dropbox_utils.delete_path(self._full_path(name))
        cache.delete(self._cache_key(name))
        cache.set(self._exists_cache_key(name), False, EXISTS_CACHE_SECONDS)

    def exists(self, name):
        cache_key = self._exists_cache_key(name)
        cached = cache.get(cache_key, _MISS)
        if cached is not _MISS:
            return cached
        result = dropbox_utils.get_metadata(self._full_path(name)) is not None
        cache.set(cache_key, result, EXISTS_CACHE_SECONDS)
        return result

    def size(self, name):
        meta = dropbox_utils.get_metadata(self._full_path(name))
        return meta['size'] if meta else 0

    def url(self, name):
        cache_key = self._cache_key(name)
        cached = cache.get(cache_key, _MISS)
        if cached is not _MISS:
            return cached
        try:
            url = dropbox_utils.get_direct_link(self._full_path(name))
        except dropbox_utils.DropboxError:
            # Cache the failure too, briefly — otherwise a broken/misconfigured Dropbox app makes
            # every image on every page make 2 doomed API calls on every single request.
            cache.set(cache_key, '', FAILURE_CACHE_SECONDS)
            return ''
        cache.set(cache_key, url, LINK_CACHE_SECONDS)
        return url

    def get_accessed_time(self, name):
        raise NotImplementedError('DropboxStorage does not record access time.')

    def get_created_time(self, name):
        raise NotImplementedError('DropboxStorage does not record creation time.')

    def get_modified_time(self, name):
        raise NotImplementedError('DropboxStorage does not record modification time.')
