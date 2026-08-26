"""One-time helper: mint a new Dropbox refresh token after changing app permissions
in the App Console (Permissions tab -> check a new scope -> Submit).

Existing refresh tokens don't pick up newly-enabled scopes automatically, so re-run
this any time you add a permission in the App Console and things start failing again.

Usage:
    python get_dropbox_refresh_token.py

Then follow the printed instructions, and paste the resulting refresh token into
DROPBOX_REFRESH_TOKEN in manjunathacademy/settings.py.
"""
import json
import urllib.parse
import urllib.request

APP_KEY = 'wgg2fsw5pf16x8q'
APP_SECRET = '38dg9gi6djz3zuu'

auth_url = 'https://www.dropbox.com/oauth2/authorize?' + urllib.parse.urlencode({
    'client_id': APP_KEY,
    'response_type': 'code',
    'token_access_type': 'offline',
})

print('1. Open this URL in your browser, log into the Dropbox account to use, click Allow:')
print()
print(auth_url)
print()
code = input('2. Dropbox will show you a code on the page — paste it here: ').strip()

data = urllib.parse.urlencode({
    'code': code,
    'grant_type': 'authorization_code',
    'client_id': APP_KEY,
    'client_secret': APP_SECRET,
}).encode('utf-8')

req = urllib.request.Request('https://api.dropboxapi.com/oauth2/token', data=data, method='POST')
with urllib.request.urlopen(req) as resp:
    payload = json.loads(resp.read().decode('utf-8'))

print()
print('New refresh token (put this in DROPBOX_REFRESH_TOKEN in settings.py):')
print(payload['refresh_token'])
