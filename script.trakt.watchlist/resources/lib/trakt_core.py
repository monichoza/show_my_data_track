# -*- coding: utf-8 -*-
"""
Trakt API integration module for Kodi addon.
Handles authentication, token management, and API calls to Trakt.tv.
"""

import json
import time
import xbmcaddon
import xbmcgui
import xbmc
try:
    import urllib.request as urllib2
except ImportError:
    import urllib2

# Trakt API configuration
TRAKT_API_URL = 'https://api.trakt.tv'
CLIENT_ID = ''
CLIENT_SECRET = ''
REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'

# Token storage keys
TOKEN_KEYS = ['access_token', 'refresh_token', 'expires_at']


class TraktAPI:
    """Main class for Trakt API interactions."""
    
    def __init__(self):
        self.addon = xbmcaddon.Addon()
        self.client_id = self.addon.getSetting('client_id')
        self.client_secret = self.addon.getSetting('client_secret')
        self.access_token = self.addon.getSetting('access_token')
        self.refresh_token = self.addon.getSetting('refresh_token')
        self.expires_at = self.addon.getSetting('expires_at')
    
    def _save_tokens(self, access_token, refresh_token, expires_in):
        """Save authentication tokens to addon settings."""
        self.addon.setSetting('access_token', access_token)
        self.addon.setSetting('refresh_token', refresh_token)
        expires_at = str(int(time.time()) + expires_in)
        self.addon.setSetting('expires_at', expires_at)
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.expires_at = expires_at
    
    def is_token_valid(self):
        """Check if current access token is valid."""
        if not self.access_token or not self.expires_at:
            return False
        try:
            expires_at = int(self.expires_at)
            return time.time() < expires_at - 60  # 60 second buffer
        except (ValueError, TypeError):
            return False
    
    def _make_request(self, endpoint, data=None, method='GET'):
        """Make API request to Trakt."""
        if not self.client_id:
            self._show_error('Trakt API credentials not configured. Please set Client ID and Secret in addon settings.')
            return None
        
        # Ensure we have valid token
        if not self.is_token_valid():
            if not self.refresh_access_token():
                return None
        
        url = f'{TRAKT_API_URL}/{endpoint}'
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.access_token}',
            'trakt-api-version': '2',
            'trakt-api-key': self.client_id
        }
        
        try:
            req = urllib2.Request(url, headers=headers)
            if data:
                req.add_data(json.dumps(data).encode('utf-8'))
            req.get_method = lambda: method
            
            response = urllib2.urlopen(req, timeout=30)
            result = response.read()
            return json.loads(result.decode('utf-8'))
        except urllib2.HTTPError as e:
            if e.code == 401:
                xbmc.log('Trakt: Token expired, attempting refresh', xbmc.LOGINFO)
                if self.refresh_access_token():
                    return self._make_request(endpoint, data, method)
            elif e.code == 429:
                retry_after = e.headers.get('Retry-After', 5)
                xbmc.sleep(int(retry_after) * 1000)
                return self._make_request(endpoint, data, method)
            self._show_error(f'Trakt API error: {e.code}')
        except Exception as e:
            self._show_error(f'Connection error: {str(e)}')
        return None
    
    def _show_error(self, message):
        """Display error notification to user."""
        xbmc.log(f'Trakt Watchlist Error: {message}', xbmc.LOGERROR)
        xbmcgui.Dialog().notification('Trakt Watchlist', message, xbmcgui.NOTIFICATION_ERROR)
    
    def refresh_access_token(self):
        """Refresh the access token using refresh token."""
        if not self.refresh_token:
            xbmcgui.Dialog().ok('Trakt Authorization', 
                'Please authorize this addon with Trakt:\n\n'
                '1. Visit https://trakt.tv/oauth/authorize\n'
                '2. Enter your Client ID\n'
                '3. Allow access and get the PIN\n'
                '4. Enter the PIN below')
            return False
        
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'refresh_token',
            'refresh_token': self.refresh_token,
            'redirect_uri': REDIRECT_URI
        }
        
        try:
            url = f'{TRAKT_API_URL}/oauth/token'
            req = urllib2.Request(url, data=json.dumps(data).encode('utf-8'))
            req.add_header('Content-Type', 'application/json')
            response = urllib2.urlopen(req, timeout=30)
            result = json.loads(response.read().decode('utf-8'))
            
            self._save_tokens(
                result['access_token'],
                result['refresh_token'],
                result['expires_in']
            )
            xbmc.log('Trakt: Token refreshed successfully', xbmc.LOGINFO)
            return True
        except Exception as e:
            xbmc.log(f'Trakt: Token refresh failed: {e}', xbmc.LOGERROR)
            return False
    
    def get_authorization_url(self):
        """Get the authorization URL for device code flow."""
        data = {
            'client_id': self.client_id,
            'redirect_uri': REDIRECT_URI
        }
        
        try:
            url = f'{TRAKT_API_URL}/oauth/device/code'
            req = urllib2.Request(url, data=json.dumps(data).encode('utf-8'))
            req.add_header('Content-Type', 'application/json')
            response = urllib2.urlopen(req, timeout=30)
            result = json.loads(response.read().decode('utf-8'))
            return result.get('device_code'), result.get('user_code'), result.get('verification_url')
        except Exception as e:
            self._show_error(f'Failed to get authorization: {str(e)}')
            return None, None, None
    
    def poll_for_token(self, device_code, expires_in, interval):
        """Poll for token after user authorization."""
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': device_code,
            'grant_type': 'urn:ietf:params:oauth:grant-type:device_code',
            'redirect_uri': REDIRECT_URI
        }
        
        start_time = time.time()
        while time.time() - start_time < expires_in:
            xbmc.sleep(interval * 1000)
            
            try:
                url = f'{TRAKT_API_URL}/oauth/token'
                req = urllib2.Request(url, data=json.dumps(data).encode('utf-8'))
                req.add_header('Content-Type', 'application/json')
                response = urllib2.urlopen(req, timeout=30)
                result = json.loads(response.read().decode('utf-8'))
                
                self._save_tokens(
                    result['access_token'],
                    result['refresh_token'],
                    result['expires_in']
                )
                xbmcgui.Dialog().notification('Trakt Watchlist', 'Successfully authorized!', xbmcgui.NOTIFICATION_INFO)
                return True
            except urllib2.HTTPError as e:
                error_data = json.loads(e.read().decode('utf-8'))
                if error_data.get('error') != 'authorization_pending':
                    self._show_error(f'Authorization failed: {error_data.get("error_description")}')
                    return False
            except Exception as e:
                self._show_error(f'Authorization error: {str(e)}')
                return False
        
        self._show_error('Authorization timed out. Please try again.')
        return False
    
    def authorize_device(self):
        """Start device authorization flow."""
        device_code, user_code, verification_url = self.get_authorization_url()
        if not device_code:
            return False
        
        # Show user the code and URL
        xbmcgui.Dialog().ok('Trakt Authorization',
            f'Please authorize this addon:\n\n'
            f'1. Visit: {verification_url}\n'
            f'2. Enter code: {user_code}\n\n'
            f'This window will close when authorization is complete.')
        
        return self.poll_for_token(device_code, 600, 5)  # 10 min expiry, 5 sec interval
    
    def get_watched_movies(self):
        """Get list of watched movies from Trakt."""
        xbmc.log('Trakt: Fetching watched movies', xbmc.LOGINFO)
        return self._make_request('sync/watched/movies?extended=full')
    
    def get_watched_shows(self):
        """Get list of watched shows from Trakt."""
        xbmc.log('Trakt: Fetching watched shows', xbmc.LOGINFO)
        return self._make_request('sync/watched/shows?extended=full')
    
    def get_watched_episodes(self, show_ids=None):
        """Get detailed episode data for watched shows."""
        if show_ids is None:
            return self._make_request('sync/watched/shows?extended=full,episodes')
        else:
            # Get specific show episodes
            shows_data = []
            for show_id in show_ids:
                data = self._make_request(f'shows/{show_id}/progress/watched?extended=full')
                if data:
                    shows_data.append(data)
            return shows_data
    
    def get_collection(self, media_type='movies'):
        """Get user's collection."""
        endpoint = f'users/{self.username}/collection/{media_type}?extended=full'
        return self._make_request(endpoint)
    
    def get_user_profile(self):
        """Get user profile info."""
        return self._make_request('users/me')
    
    @property
    def username(self):
        """Get stored username."""
        return self.addon.getSetting('trakt_username') or 'me'


def get_trakt():
    """Get Trakt API instance."""
    return TraktAPI()