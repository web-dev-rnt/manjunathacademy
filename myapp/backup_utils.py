import os
import re
import shutil

from django.db import connection
from django.utils import timezone

from . import dropbox_utils
from .dropbox_utils import DropboxError

BACKUP_ROOT = '/Manjunath Academy'
DB_BACKUP_ROOT = f'{BACKUP_ROOT}/Database'
DB_HISTORY_FOLDER = f'{DB_BACKUP_ROOT}/files'
DB_LATEST_PATH = f'{DB_BACKUP_ROOT}/db_latest.sqlite3'

BACKUP_NAME_RE = re.compile(r'^db_(\d{8})_(\d{6})\.sqlite3$')


def _sqlite_path():
    if connection.vendor != 'sqlite':
        return None
    db_path = connection.settings_dict.get('NAME')
    if db_path and os.path.isfile(db_path):
        return str(db_path)
    return None


def run_full_backup(dropbox_settings):
    """Uploads a timestamped copy of the SQLite database to Dropbox.

    Media (banners, course videos, e-library PDFs, thumbnails, etc.) is uploaded straight to
    Dropbox the moment it's uploaded in the admin panel, so there's nothing further to back up here.
    """
    if not dropbox_utils.is_configured():
        return False, 'Dropbox is not configured.'

    db_path = _sqlite_path()
    if not db_path:
        return False, 'No SQLite database file was found to back up.'

    timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
    try:
        dropbox_utils.upload_file(f'{DB_HISTORY_FOLDER}/db_{timestamp}.sqlite3', db_path)
        dropbox_utils.upload_file(DB_LATEST_PATH, db_path)
    except DropboxError as exc:
        return False, str(exc)

    dropbox_settings.last_backup_at = timezone.now()
    dropbox_settings.last_backup_status = 'Database backed up successfully.'
    dropbox_settings.save(update_fields=['last_backup_at', 'last_backup_status'])

    return True, dropbox_settings.last_backup_status


def list_db_backups():
    """Returns database backups from Manjunath Academy/Database/files, newest first, as
    [{'filename', 'date', 'time'}, ...] parsed from the db_YYYYMMDD_HHMMSS.sqlite3 naming."""
    entries = dropbox_utils.list_folder(DB_HISTORY_FOLDER)
    backups = []
    for entry in entries:
        match = BACKUP_NAME_RE.match(entry['name'])
        if not match:
            continue
        date_part, time_part = match.groups()
        backups.append({
            'filename': entry['name'],
            'date': f'{date_part[0:4]}-{date_part[4:6]}-{date_part[6:8]}',
            'time': f'{time_part[0:2]}:{time_part[2:4]}:{time_part[4:6]}',
        })
    backups.sort(key=lambda b: b['filename'], reverse=True)
    return backups


def restore_database(dropbox_settings, filename=None):
    """Downloads a database backup from Dropbox and restores it, keeping a safety copy of the current file.

    Defaults to the latest backup when `filename` isn't given. Since every FileField/ImageField now
    resolves its URL straight from Dropbox, restoring the database alone brings back all media too —
    there's no separate media restore step.
    """
    if not dropbox_utils.is_configured():
        return False, 'Dropbox is not configured.'
    if connection.vendor != 'sqlite':
        return False, 'Restore is only supported when the site is using a SQLite database.'

    dropbox_path = f'{DB_HISTORY_FOLDER}/{filename}' if filename else DB_LATEST_PATH

    db_path = connection.settings_dict.get('NAME')
    tmp_path = f'{db_path}.restore_tmp'

    try:
        dropbox_utils.download_file(dropbox_path, tmp_path)
    except DropboxError as exc:
        return False, str(exc)

    with open(tmp_path, 'rb') as f:
        header = f.read(16)
    if header != b'SQLite format 3\x00':
        os.remove(tmp_path)
        return False, 'The downloaded file is not a valid SQLite database — restore aborted.'

    safety_path = f'{db_path}.before_restore_{timezone.now().strftime("%Y%m%d_%H%M%S")}'
    if os.path.isfile(db_path):
        shutil.copy2(db_path, safety_path)

    shutil.move(tmp_path, db_path)
    return True, f'Database restored from {filename or "the latest backup"}. Your previous database was saved as {os.path.basename(safety_path)}. Restart the app for the change to fully take effect.'


def delete_all_backups():
    """Permanently deletes every database backup (history + latest) from Dropbox. Does not touch media."""
    if not dropbox_utils.is_configured():
        return False, 'Dropbox is not configured.'
    try:
        dropbox_utils.delete_path(DB_BACKUP_ROOT)
    except DropboxError as exc:
        return False, str(exc)
    return True, 'All database backups have been deleted from Dropbox.'
