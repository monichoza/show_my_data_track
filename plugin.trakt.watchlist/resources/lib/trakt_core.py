# -*- coding: utf-8 -*-
"""
Trakt API integration using script.module.trakt library.
Simplified wrapper for fetching watched movies and shows.
"""

import xbmc
import xbmcaddon
import xbmcgui
from trakt import Trakt


class TraktWatchlist:
    """Simplified Trakt API wrapper using script.module.trakt."""
    
    def __init__(self):
        self.addon = xbmcaddon.Addon()
    
    def configure(self):
        """Configure Trakt library with credentials."""
        client_id = self.addon.getSetting('trakt_client_id')
        client_secret = self.addon.getSetting('trakt_client_secret')
        access_token = self.addon.getSetting('trakt_access_token')
        
        Trakt.configuration.defaults.client(
            id=client_id,
            secret=client_secret
        )
        if access_token:
            Trakt.oauth.token(access_token)
    
    def _get_username(self):
        """Get username from settings or use 'me'."""
        return self.addon.getSetting('trakt_username') or 'me'
    
    def get_watched_movies(self):
        """Get list of watched movies from Trakt."""
        try:
            self.configure()
            
            movies_response = Trakt['sync/watched'].movies
            if not movies_response:
                return []
            
            result = []
            for movie in movies_response.values:
                result.append({
                    'title': getattr(movie, 'title', 'Unknown'),
                    'year': getattr(movie, 'year', ''),
                    'watched_at': getattr(movie, 'watched_at', ''),
                    'ids': {
                        'trakt': getattr(movie, 'trakt', ''),
                        'imdb': getattr(movie, 'imdb', ''),
                        'tmdb': getattr(movie, 'tmdb', ''),
                    }
                })
            return result
        except Exception as e:
            xbmc.log(f'Trakt Watchlist: Error fetching movies - {e}', xbmc.LOGERROR)
            return []
    
    def get_watched_shows(self):
        """Get list of watched shows from Trakt."""
        try:
            self.configure()
            
            shows_response = Trakt['sync/watched'].shows
            if not shows_response:
                return []
            
            result = []
            for show in shows_response.values:
                # Count total episodes
                episode_count = 0
                seasons_data = []
                for season in show.seasons:
                    ep_count = len(season.episodes)
                    episode_count += ep_count
                    seasons_data.append({
                        'number': season.number,
                        'episode_count': ep_count
                    })
                
                result.append({
                    'title': getattr(show, 'title', 'Unknown'),
                    'year': getattr(show, 'year', ''),
                    'episode_count': episode_count,
                    'seasons': seasons_data,
                    'ids': {
                        'trakt': getattr(show, 'trakt', ''),
                        'tvdb': getattr(show, 'tvdb', ''),
                        'imdb': getattr(show, 'imdb', ''),
                        'tmdb': getattr(show, 'tmdb', ''),
                    }
                })
            return result
        except Exception as e:
            xbmc.log(f'Trakt Watchlist: Error fetching shows - {e}', xbmc.LOGERROR)
            return []
    
    def get_user_profile(self):
        """Get user profile info."""
        try:
            self.configure()
            user = Trakt['users'].profile(username=self._get_username())
            return {
                'username': getattr(user, 'username', 'Unknown'),
                'name': getattr(user, 'name', ''),
            }
        except Exception as e:
            xbmc.log(f'Trakt Watchlist: Error fetching profile - {e}', xbmc.LOGERROR)
            return None
    
    def is_configured(self):
        """Check if Trakt is configured with credentials."""
        client_id = self.addon.getSetting('trakt_client_id')
        client_secret = self.addon.getSetting('trakt_client_secret')
        return bool(client_id and client_secret)


def get_trakt_watchlist():
    """Get TraktWatchlist instance."""
    return TraktWatchlist()