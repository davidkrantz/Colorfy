"""Script that generates a refresh token for a specific user."""
import os
import sys
import spotipy.util as util
import json


if len(sys.argv) == 2:
     username = str(sys.argv[1])
else:
    print('Usage: {} username'.format(sys.argv[0]))
    sys.exit(1)

scope = 'user-read-currently-playing user-read-playback-state'

# Get tokens from Spotify.
try:
    util.prompt_for_user_token(username, scope)
except:
    raise RuntimeError('Could not fetch token.')

# Print refresh token.
with open('.cache-{}'.format(username)) as json_file:
    data = json.load(json_file)
    print('Refresh token for {}: {}'.format(username, data['refresh_token']))
