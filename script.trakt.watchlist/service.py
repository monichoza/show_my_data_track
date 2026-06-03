# -*- coding: utf-8 -*-
"""
Background service for Trakt Watchlist addon.
Provides authentication with script.trakt integration.
"""

import xbmc
import xbmcaddon
import xbmcgui
from resources.lib.trakt_core import get_trakt_watchlist


class TraktWatchlistService:
    """Background service for Trakt API integration."""
    
    def __init__(self):
        self.addon = xbmcaddon.Addon()
        self.trakt = get_trakt_watchlist()
        self.monitor = xbmc.Monitor()
    
    def log(self, message):
        """Log message to Kodi log."""
        xbmc.log(f'TraktWatchlist Service: {message}', xbmc.LOGINFO)
    
    def run(self):
        """Main service loop."""
        self.log('Service started')
        
        if not self.trakt.is_configured():
            self.log('Trakt not configured, waiting for setup...')
        
        while not self.monitor.abortRequested():
            if self.monitor.waitForAbort(3600):  # Check every hour
                break
        
        self.log('Service stopped')


def router(argv):
    """Route commands from the service."""
    if len(argv) < 2:
        return
    
    command = argv[1].lower()
    trakt = get_trakt_watchlist()
    
    if command == 'auth':
        if trakt.is_configured():
            xbmcgui.Dialog().notification('Trakt Watchlist', 'Already configured', xbmcgui.NOTIFICATION_INFO)
        else:
            xbmcgui.Dialog().ok('Trakt Watchlist', 'Please configure your Trakt credentials in settings first.')
    elif command == 'status':
        if trakt.is_configured():
            xbmcgui.Dialog().notification('Trakt Watchlist', 'Connected to Trakt', xbmcgui.NOTIFICATION_INFO)
        else:
            xbmcgui.Dialog().notification('Trakt Watchlist', 'Not configured - Please set up in settings', xbmcgui.NOTIFICATION_WARNING)
    elif command == 'movies':
        return trakt.get_watched_movies()
    elif command == 'shows':
        return trakt.get_watched_shows()
    
    return None


if __name__ == '__main__':
    service = TraktWatchlistService()
    service.run()