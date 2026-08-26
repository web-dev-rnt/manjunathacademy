import json
import time
import urllib.error
import urllib.parse
import urllib.request

from django.conf import settings

TOKEN_URL = 'https://api.dropboxapi.com/oauth2/token'
UPLOAD_URL = 'https://content.dropboxapi.com/2/files/upload'
DOWNLOAD_URL = 'https://content.dropboxapi.com/2/files/download'
LIST_FOLDER_URL = 'https://api.dropboxapi.com/2/files/list_folder'
LIST_FOLDER_CONTINUE_URL = 'https://api.dropboxapi.com/2/files/list_folder/continue'
DELETE_URL = 'https://api.dropboxapi.com/2/files/delete_v2'
ACCOUNT_URL = 'https://api.dropboxapi.com/2/users/get_current_account'
GET_METADATA_URL = 'https://api.dropboxapi.com/2/files/get_metadata'
CREATE_SHARED_LINK_URL = 'https://api.dropboxapi.com/2/sharing/create_shared_link_with_settings'
LIST_SHARED_LINKS_URL = 'https://api.dropboxapi.com/2/sharing/list_shared_links'

_token_cache = {'token': None, 'expires_at': 0}


class DropboxError(Exception):
    pass


def _http_error_detail(exc):
    try:
        return exc.read().decode('utf-8', errors='ignore')
    except Exception:
        return str(exc)


def is_configured():
    return bool(settings.DROPBOX_APP_KEY and settings.DROPBOX_APP_SECRET and settings.DROPBOX_REFRESH_TOKEN)


def _get_access_token():
    if _token_cache['token'] and time.time() < _token_cache['expires_at'] - 60:
        return _token_cache['token']

    if not is_configured():
        raise DropboxError('Dropbox app key/secret/refresh token are not configured.')

    data = urllib.parse.urlencode({
        'grant_type': 'refresh_token',
        'refresh_token': settings.DROPBOX_REFRESH_TOKEN,
        'client_id': settings.DROPBOX_APP_KEY,
        'client_secret': settings.DROPBOX_APP_SECRET,
    }).encode('utf-8')
    req = urllib.request.Request(TOKEN_URL, data=data, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            payload = json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as exc:
        raise DropboxError(f'Could not refresh Dropbox access token: {_http_error_detail(exc)}')
    except Exception as exc:
        raise DropboxError(f'Could not refresh Dropbox access token: {exc}')

    token = payload.get('access_token')
    if not token:
        raise DropboxError('Dropbox did not return an access token.')
    _token_cache['token'] = token
    _token_cache['expires_at'] = time.time() + payload.get('expires_in', 14400)
    return token


def _auth_headers(extra=None):
    headers = {'Authorization': f'Bearer {_get_access_token()}'}
    if extra:
        headers.update(extra)
    return headers


def test_connection():
    req = urllib.request.Request(
        ACCOUNT_URL,
        data=b'null',
        headers=_auth_headers({'Content-Type': 'application/json'}),
        method='POST',
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as exc:
        raise DropboxError(f'Could not connect to Dropbox: {_http_error_detail(exc)}')
    except Exception as exc:
        raise DropboxError(f'Could not connect to Dropbox: {exc}')


def upload_bytes(dropbox_path, data):
    api_arg = json.dumps({'path': dropbox_path, 'mode': 'overwrite', 'autorename': False, 'mute': True})
    req = urllib.request.Request(
        UPLOAD_URL,
        data=data,
        headers=_auth_headers({
            'Dropbox-API-Arg': api_arg,
            'Content-Type': 'application/octet-stream',
        }),
        method='POST',
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as exc:
        raise DropboxError(f'Upload failed for {dropbox_path}: {_http_error_detail(exc)}')


def upload_file(dropbox_path, local_path):
    with open(local_path, 'rb') as f:
        return upload_bytes(dropbox_path, f.read())


def download_bytes(dropbox_path):
    api_arg = json.dumps({'path': dropbox_path})
    req = urllib.request.Request(
        DOWNLOAD_URL,
        data=b'',
        headers=_auth_headers({'Dropbox-API-Arg': api_arg}),
        method='POST',
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            return resp.read()
    except urllib.error.HTTPError as exc:
        raise DropboxError(f'Download failed for {dropbox_path}: {_http_error_detail(exc)}')


def download_file(dropbox_path, local_path):
    content = download_bytes(dropbox_path)
    with open(local_path, 'wb') as f:
        f.write(content)


def _post_json(url, body):
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode('utf-8'),
        headers=_auth_headers({'Content-Type': 'application/json'}),
        method='POST',
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode('utf-8'))


def list_folder(path, recursive=False):
    """Returns [{name, path_display, server_modified}, ...] for files inside `path`.

    Returns an empty list if the folder doesn't exist yet (e.g. no backups taken so far).
    """
    try:
        payload = _post_json(LIST_FOLDER_URL, {'path': path, 'recursive': recursive})
    except urllib.error.HTTPError as exc:
        detail = _http_error_detail(exc)
        if 'path/not_found' in detail:
            return []
        raise DropboxError(f'Could not list {path}: {detail}')
    except Exception as exc:
        raise DropboxError(f'Could not list {path}: {exc}')

    entries = list(payload.get('entries', []))
    while payload.get('has_more'):
        payload = _post_json(LIST_FOLDER_CONTINUE_URL, {'cursor': payload['cursor']})
        entries.extend(payload.get('entries', []))

    files = [e for e in entries if e.get('.tag') == 'file']
    return [
        {'name': e['name'], 'path_display': e.get('path_display', e['name']), 'server_modified': e.get('server_modified', '')}
        for e in files
    ]


def delete_path(path):
    """Deletes a file or folder (and everything inside it) at `path`. No-ops if it doesn't exist."""
    try:
        _post_json(DELETE_URL, {'path': path})
    except urllib.error.HTTPError as exc:
        detail = _http_error_detail(exc)
        if 'path_lookup/not_found' in detail:
            return
        raise DropboxError(f'Could not delete {path}: {detail}')
    except Exception as exc:
        raise DropboxError(f'Could not delete {path}: {exc}')


def get_metadata(path):
    """Returns file metadata (dict with at least 'size'), or None if the path doesn't exist."""
    try:
        return _post_json(GET_METADATA_URL, {'path': path})
    except urllib.error.HTTPError as exc:
        detail = _http_error_detail(exc)
        if 'not_found' in detail:
            return None
        raise DropboxError(f'Could not get metadata for {path}: {detail}')
    except Exception as exc:
        raise DropboxError(f'Could not get metadata for {path}: {exc}')


def _to_raw_url(url):
    """Rewrites a Dropbox shared-link URL to serve raw file bytes (for <img>/<video> embedding)
    instead of Dropbox's HTML preview page."""
    parsed = urllib.parse.urlsplit(url)
    query = dict(urllib.parse.parse_qsl(parsed.query))
    query.pop('dl', None)
    query['raw'] = '1'
    return urllib.parse.urlunsplit((parsed.scheme, parsed.netloc, parsed.path, urllib.parse.urlencode(query), parsed.fragment))


def get_direct_link(path):
    """Returns a permanent, directly-embeddable URL for a file, creating a shared link if needed."""
    try:
        payload = _post_json(LIST_SHARED_LINKS_URL, {'path': path, 'direct_only': True})
        links = payload.get('links') or []
        if links:
            return _to_raw_url(links[0]['url'])
    except urllib.error.HTTPError as exc:
        raise DropboxError(f'Could not list shared links for {path}: {_http_error_detail(exc)}')
    except Exception as exc:
        raise DropboxError(f'Could not list shared links for {path}: {exc}')

    try:
        payload = _post_json(CREATE_SHARED_LINK_URL, {'path': path})
        return _to_raw_url(payload['url'])
    except urllib.error.HTTPError as exc:
        detail = _http_error_detail(exc)
        if 'shared_link_already_exists' in detail:
            try:
                existing_url = json.loads(detail)['error']['shared_link_already_exists']['metadata']['url']
                return _to_raw_url(existing_url)
            except Exception:
                pass
        raise DropboxError(f'Could not create shared link for {path}: {detail}')
    except Exception as exc:
        raise DropboxError(f'Could not create shared link for {path}: {exc}')
