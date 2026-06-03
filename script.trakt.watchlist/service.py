# -*- coding: utf-8 -*-
"""
Background service for Trakt Watchlist addon.
Provides authentication with script.trakt integration.
"""

import xbmc
import xbmcaddon
import xbmcgui
from resources.lib import trakt_core


class TraktWatchlistService:
    """Background service for Trakt API integration."""
    
    def __init__(self):
        self.addon = xbmcaddon.Addon()
        self.trakt = trakt_core.get_trakt()
        self.monitor = xbmc.Monitor()
        self.last_refresh = 0
    
    def log(self, message):
        """Log message to Kodi log."""
        xbmc.log(f'TraktWatchlist Service: {message}', xbmc.LOGINFO)
    
    def run(self):
        """Main service loop."""
        self.log('Service started')
        
        # Initial data fetch
        if self.addon.getSetting('auto_refresh') == 'true':
            self.fetch_all_data()
        
        # Service loop
        while not self.monitor.abortRequested():
            # Check for refresh interval
            refresh_interval = int(self.addon.getSetting('refresh_interval') or 6) * 3600
            if xbmc.getLastChanged('systemdate') != self.last_refresh:
                if self.monitor.waitForAbort(60):  # Check every minute
                    break
                self.last_refresh = xbmc.getLastChanged('systemdate')
                
                # Perform refresh if needed
                if self.addon.getSetting('auto_refresh') == 'true':
                    self.fetch_all_data()
            else:
                if self.monitor.waitForAbort(300):  # 5 min default
                    break
        
        self.log('Service stopped')
    
    def fetch_all_data(self):
        """Fetch all data from Trakt."""
        self.log('Fetching data from Trakt...')
        
        # Fetch movies
        movies = self.trakt.get_watched_movies()
        if movies:
            self.log(f'Fetched {len(movies)} watched movies')
        
        # Fetch shows
        shows = self.trakt.get_watched_shows()
        if shows:
            self.log(f'Fetched {len(shows)} watched shows')
        
        return movies, shows


def router(argv):
    """
    Route commands from the service.
    Handles calls from script.trakt integration.
    """
    if len(argv) < 2:
        return
    
    command = argv[1].lower()
    trakt = trakt_core.get_trakt()
    
    if command == 'auth':
        trakt.authorize_device()
    elif command == 'refresh':
        trakt.refresh_access_token()
    elif command == 'movies':
        return trakt.get_watched_movies()
    elif command == 'shows':
        return trakt.get_watched_shows()
    elif command == 'status':
        if trakt.is_token_valid():
            xbmcgui.Dialog().notification('Trakt Watchlist', 'Connected to Trakt', xbmcgui.NOTIFICATION_INFO)
        else:
            xbmcgui.Dialog().notification('Trakt Watchlist', 'Not connected - Please authorize', xbmcgui.NOTIFICATION_WARNING)
    
    return None


if __name__ == '__main__':
    service = TraktWatchlistService()
    service.run()