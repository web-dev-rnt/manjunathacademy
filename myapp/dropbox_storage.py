from django.core.cache import cache
from django.core.files.base import ContentFile
from django.core.files.storage import Storage
from django.utils.deconstruct import deconstructible

from . import dropbox_utils

ROOT = '/Manjunath Academy/Media'
LINK_CACHE_SECONDS = 60 * 60 * 24 * 30  # shared links never expire, so cache them for a month


@deconstructible
class DropboxStorage(Storage):
    """Stores every upload (banners, course videos, e-library PDFs, thumbnails, etc.) directly on
    Dropbox instead of the local (ephemeral, on Railway) disk. FieldFile.name stays a short relative
    path like 'courses/thumb1.jpg' — that name plus ROOT is all that's needed to resolve the Dropbox
    path, so a restored database renders working image/video URLs with no separate media restore step."""

    def _full_path(self, name):
        return f'{ROOT}/{name.lstrip("/")}'

    def _save(self, name, content):
        content.seek(0)
        dropbox_utils.upload_bytes(self._full_path(name), content.read())
        return name

    def _open(self, name, mode='rb'):
        return ContentFile(dropbox_utils.download_bytes(self._full_path(name)), name=name)

    def delete(self, name):
        dropbox_utils.delete_path(self._full_path(name))
        cache.delete(f'dbx_url:{name}')

    def exists(self, name):
        return dropbox_utils.get_metadata(self._full_path(name)) is not None

    def size(self, name):
        meta = dropbox_utils.get_metadata(self._full_path(name))
        return meta['size'] if meta else 0

    def url(self, name):
        cache_key = f'dbx_url:{name}'
        cached = cache.get(cache_key)
        if cached:
            return cached
        try:
            url = dropbox_utils.get_direct_link(self._full_path(name))
        except dropbox_utils.DropboxError:
            return ''
        cache.set(cache_key, url, LINK_CACHE_SECONDS)
        return url

    def get_accessed_time(self, name):
        raise NotImplementedError('DropboxStorage does not record access time.')

    def get_created_time(self, name):
        raise NotImplementedError('DropboxStorage does not record creation time.')

    def get_modified_time(self, name):
        raise NotImplementedError('DropboxStorage does not record modification time.')
