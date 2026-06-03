# -*- coding: utf-8 -*-
"""
Trakt API integration using script.module.trakt library.
Simplified wrapper for fetching watched movies and shows.
"""

import xbmc
import xbmcaddon
import xbmcgui
import trakt
from trakt.users import User
from trakt.movies import Movie
from trakt.tv import TVShow
from trakt.media_map import MediaMap


class TraktWatchlist:
    """Simplified Trakt API wrapper using script.module.trakt."""
    
    def __init__(self):
        self.addon = xbmcaddon.Addon()
        self.client_id = self.addon.getSetting('trakt_client_id')
        self.client_secret = self.addon.getSetting('trakt_client_secret')
        self.username = self.addon.getSetting('trakt_username')
    
    def configure(self):
        """Configure Trakt library with credentials."""
        trakt.api_key(self.client_id)
        trakt.client_secret(self.client_secret)
        
        access_token = self.addon.getSetting('trakt_access_token')
        if access_token:
            trakt.oauth.token(access_token)
    
    def get_watched_movies(self):
        """Get list of watched movies from Trakt."""
        try:
            self.configure()
            if not self.username:
                self.username = 'me'
            
            user = User(self.username)
            movies = user.watched_movies
            return self._parse_movies(movies) if movies else []
        except Exception as e:
            xbmc.log(f'Trakt Watchlist: Error fetching movies - {e}', xbmc.LOGERROR)
            return []
    
    def get_watched_shows(self):
        """Get list of watched shows from Trakt."""
        try:
            self.configure()
            if not self.username:
                self.username = 'me'
            
            user = User(self.username)
            shows = user.watched_shows
            return self._parse_shows(shows) if shows else []
        except Exception as e:
            xbmc.log(f'Trakt Watchlist: Error fetching shows - {e}', xbmc.LOGERROR)
            return []
    
    def _parse_movies(self, movies):
        """Parse movie objects into dictionaries."""
        result = []
        for movie in movies:
            result.append({
                'title': getattr(movie, 'title', 'Unknown'),
                'year': getattr(movie, 'year', ''),
                'plays': getattr(movie, 'plays', 0),
                'last_watched': getattr(movie, 'last_watched_at', ''),
                'ids': {
                    'trakt': getattr(movie, 'trakt', ''),
                    'imdb': getattr(movie, 'imdb', ''),
                    'tmdb': getattr(movie, 'tmdb', ''),
                }
            })
        return result
    
    def _parse_shows(self, shows):
        """Parse show objects into dictionaries."""
        result = []
        for show in shows:
            result.append({
                'title': getattr(show, 'title', 'Unknown'),
                'year': getattr(show, 'year', ''),
                'episode_count': getattr(show, 'episode_count', 0),
                'seasons': getattr(show, 'seasons', []),
                'ids': {
                    'trakt': getattr(show, 'trakt', ''),
                    'tvdb': getattr(show, 'tvdb', ''),
                    'imdb': getattr(show, 'imdb', ''),
                    'tmdb': getattr(show, 'tmdb', ''),
                }
            })
        return result
    
    def get_user_profile(self):
        """Get user profile info."""
        try:
            self.configure()
            user = User('me')
            return {
                'username': user.username,
                'name': getattr(user, 'name', ''),
                'joined_at': getattr(user, 'created_at', '')
            }
        except Exception as e:
            xbmc.log(f'Trakt Watchlist: Error fetching profile - {e}', xbmc.LOGERROR)
            return None
    
    def is_configured(self):
        """Check if Trakt is configured with credentials."""
        return bool(self.client_id and self.client_secret)


def get_trakt_watchlist():
    """Get TraktWatchlist instance."""
    return TraktWatchlist()