# -*- coding: utf-8 -*-
"""
Main entry point for Trakt Watchlist Kodi addon.
Displays watched movies and shows from user's Trakt account.
Uses script.module.trakt for API calls.
"""

import sys
import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
from resources.lib.trakt_core import get_trakt_watchlist

ADDON = xbmcaddon.Addon()
ADDON_NAME = ADDON.getAddonInfo('name')
ADDON_HANDLE = int(sys.argv[1])
BASE_URL = sys.argv[0]


def build_menu():
    """Build the main menu."""
    items = [
        ('Watched Movies', 'movies', 'DefaultMovieTitle.png'),
        ('Watched TV Shows', 'shows', 'DefaultTVShows.png'),
        ('Trakt Status', 'status', 'DefaultAddonService.png'),
    ]
    
    for title, action, icon in items:
        li = xbmcgui.ListItem(label=title)
        li.setArt({'icon': icon})
        url = f'{BASE_URL}?action={action}'
        xbmcplugin.addDirectoryItem(ADDON_HANDLE, url, li, isFolder=True)
    
    xbmcplugin.endOfDirectory(ADDON_HANDLE)


def display_movies(movies):
    """Display watched movies."""
    if not movies:
        xbmcgui.Dialog().notification(ADDON_NAME, 'No watched movies found', xbmcgui.NOTIFICATION_INFO)
        xbmcplugin.endOfDirectory(ADDON_HANDLE)
        return
    
    for movie in movies:
        title = movie.get('title', 'Unknown')
        year = movie.get('year', '')
        plays = movie.get('plays', 0)
        
        label = f'{title} ({year})' if year else title
        if plays > 1:
            label += f' [x{plays}]'
        
        li = xbmcgui.ListItem(label=label)
        url = f'plugin://script.trakt/sync?action=play&type=movie&id={movie.get("ids", {}).get("trakt", "")}'
        xbmcplugin.addDirectoryItem(ADDON_HANDLE, url, li, isFolder=False)
    
    xbmcplugin.endOfDirectory(ADDON_HANDLE, cacheToDisc=False)


def display_shows(shows):
    """Display watched TV shows."""
    if not shows:
        xbmcgui.Dialog().notification(ADDON_NAME, 'No watched shows found', xbmcgui.NOTIFICATION_INFO)
        xbmcplugin.endOfDirectory(ADDON_HANDLE)
        return
    
    for show in shows:
        title = show.get('title', 'Unknown')
        year = show.get('year', '')
        episode_count = show.get('episode_count', 0)
        
        label = f'{title} ({year})' if year else title
        label += f' [{episode_count} eps]'
        
        li = xbmcgui.ListItem(label=label)
        show_id = show.get('ids', {}).get('trakt', '')
        url = f'{BASE_URL}?action=show_detail&id={show_id}' if show_id else ''
        xbmcplugin.addDirectoryItem(ADDON_HANDLE, url, li, isFolder=bool(show_id))
    
    xbmcplugin.endOfDirectory(ADDON_HANDLE, cacheToDisc=False)


def router(paramstring):
    """Route commands based on parameters."""
    params = dict(xbmc.parseQuery(paramstring))
    action = params.get('action', '')
    
    trakt = get_trakt_watchlist()
    
    if not action:
        build_menu()
        return
    
    if action == 'movies':
        dp = xbmcgui.DialogProgress()
        dp.create(ADDON_NAME, 'Loading movies...')
        movies = trakt.get_watched_movies()
        dp.close()
        display_movies(movies)
    
    elif action == 'shows':
        dp = xbmcgui.DialogProgress()
        dp.create(ADDON_NAME, 'Loading shows...')
        shows = trakt.get_watched_shows()
        dp.close()
        display_shows(shows)
    
    elif action == 'status':
        if trakt.is_configured():
            profile = trakt.get_user_profile()
            if profile:
                xbmcgui.Dialog().ok(ADDON_NAME, f"Connected!\nUsername: {profile.get('username', 'N/A')}")
            else:
                xbmcgui.Dialog().notification(ADDON_NAME, 'Connected to Trakt', xbmcgui.NOTIFICATION_INFO)
        else:
            xbmcgui.Dialog().ok(ADDON_NAME, 'Not configured.\n\nPlease enter your Trakt Client ID and Secret in settings.')
    
    elif action == 'settings':
        ADDON.openSettings()
        build_menu()
    
    else:
        build_menu()


if __name__ == '__main__':
    router(sys.argv[2][1:] if len(sys.argv) > 2 else '')