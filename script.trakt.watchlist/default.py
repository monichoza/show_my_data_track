# -*- coding: utf-8 -*-
"""
Main entry point for Trakt Watchlist Kodi addon.
Displays watched movies and shows from user's Trakt account.
"""

import sys
import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
from resources.lib import trakt_core

# Get addon info
ADDON = xbmcaddon.Addon()
ADDON_NAME = ADDON.getAddonInfo('name')
ADDON_HANDLE = int(sys.argv[1])
BASE_URL = sys.argv[0]


def build_menu():
    """Build the main menu."""
    items = [
        ('Watched Movies', 'movies', 'DefaultMovieTitle.png'),
        ('Watched TV Shows', 'shows', 'DefaultTVShows.png'),
        ('Sync with Trakt', 'sync', 'DefaultAddonService.png'),
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
        
        # Get poster if available
        images = movie.get('images', {})
        poster = images.get('poster', {}).get('thumb', '') or images.get('poster', '')
        
        label = f'{title} ({year})' if year else title
        if plays > 1:
            label += f' [x{plays}]'
        
        li = xbmcgui.ListItem(label=label)
        if poster:
            li.setArt({'thumb': poster, 'poster': poster})
        
        # Build playable URL
        movie_id = movie.get('ids', {}).get('trakt')
        if movie_id:
            url = f'plugin://script.trakt/sync?action=play&type=movie&id={movie_id}'
        else:
            url = ''
        
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
        seasons = show.get('seasons', [])
        episode_count = sum(len(s.get('episodes', [])) for s in seasons)
        
        # Get poster if available
        images = show.get('images', {})
        poster = images.get('poster', {}).get('thumb', '') or images.get('poster', '')
        
        label = f'{title} ({year})' if year else title
        label += f' [{episode_count} eps]'
        
        li = xbmcgui.ListItem(label=label)
        if poster:
            li.setArt({'thumb': poster, 'poster': poster})
        
        # Build URL to show episodes
        show_id = show.get('ids', {}).get('trakt')
        url = f'{BASE_URL}?action=show_detail&id={show_id}' if show_id else ''
        
        xbmcplugin.addDirectoryItem(ADDON_HANDLE, url, li, isFolder=True)
    
    xbmcplugin.endOfDirectory(ADDON_HANDLE, cacheToDisc=False)


def display_show_detail(show_id, show_data=None):
    """Display episodes for a specific show."""
    if not show_data:
        # Fetch show data if not provided
        trakt = trakt_core.get_trakt()
        # This would need the full episode data
        return
    
    seasons = show_data.get('seasons', [])
    show_title = show_data.get('title', 'Unknown Show')
    
    for season in seasons:
        season_num = season.get('number', 0)
        episodes = season.get('episodes', [])
        
        for episode in episodes:
            ep_num = episode.get('number', 0)
            title = episode.get('title', f'Episode {ep_num}')
            plays = episode.get('plays', 0)
            
            label = f'S{season_num:02d}E{ep_num:02d} - {title}'
            if plays > 1:
                label += f' [x{plays}]'
            
            li = xbmcgui.ListItem(label=label)
            url = f'plugin://script.trakt/sync?action=play&type=episode&show={show_id}&season={season_num}&episode={ep_num}'
            
            xbmcplugin.addDirectoryItem(ADDON_HANDLE, url, li, isFolder=False)
    
    xbmcplugin.setPluginCategory(ADDON_HANDLE, show_title)
    xbmcplugin.endOfDirectory(ADDON_HANDLE, cacheToDisc=False)


def sync_with_trakt():
    """Sync data with Trakt."""
    trakt = trakt_core.get_trakt()
    
    # Check if authorized
    if not trakt.is_token_valid():
        xbmcgui.Dialog().ok(ADDON_NAME,
            'Not connected to Trakt.\n\n'
            'Please configure your Client ID and Secret in settings, '
            'then authorize the addon.')
        
        # Open settings
        ADDON.openSettings()
        return
    
    # Show progress dialog
    dp = xbmcgui.DialogProgress()
    dp.create(ADDON_NAME, 'Syncing with Trakt...')
    dp.update(10, 'Fetching watched movies...')
    
    movies = trakt.get_watched_movies()
    dp.update(50, 'Fetching watched shows...')
    
    shows = trakt.get_watched_shows()
    dp.update(100, 'Sync complete!')
    dp.close()
    
    # Show results
    msg = f'Movies: {len(movies) if movies else 0}\nShows: {len(shows) if shows else 0}'
    xbmcgui.Dialog().ok(ADDON_NAME, msg)


def router(paramstring):
    """Route commands based on parameters."""
    params = dict(xbmc.parseQuery(paramstring))
    action = params.get('action', '')
    
    trakt = trakt_core.get_trakt()
    
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
    
    elif action == 'show_detail':
        show_id = params.get('id')
        # For now, show a simple list - full implementation would fetch episodes
        xbmcgui.Dialog().notification(ADDON_NAME, f'Show ID: {show_id}', xbmcgui.NOTIFICATION_INFO)
    
    elif action == 'sync':
        sync_with_trakt()
        build_menu()
    
    elif action == 'auth':
        trakt.authorize_device()
        build_menu()
    
    elif action == 'settings':
        ADDON.openSettings()
        build_menu()
    
    else:
        xbmc.log(f'Unknown action: {action}', xbmc.LOGWARNING)
        build_menu()


if __name__ == '__main__':
    router(sys.argv[2][1:] if len(sys.argv) > 2 else '')