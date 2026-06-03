# -*- coding: utf-8 -*-
"""
Video plugin entry point for Trakt Watchlist Kodi addon.
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


def get_url(action, **kwargs):
    """Build plugin URL with parameters."""
    params = [f'action={action}']
    for key, value in kwargs.items():
        params.append(f'{key}={value}')
    return f'{BASE_URL}?{"&".join(params)}'


def build_menu():
    """Build the main menu."""
    items = [
        ('Watched Movies', 'movies', 'DefaultMovies.png'),
        ('Watched TV Shows', 'shows', 'DefaultTVShows.png'),
        ('Trakt Status', 'status', 'DefaultAddonService.png'),
    ]
    
    for title, action, icon in items:
        li = xbmcgui.ListItem(label=title)
        li.setArt({'icon': icon, 'thumb': icon})
        xbmcplugin.addDirectoryItem(ADDON_HANDLE, get_url(action), li, isFolder=True)
    
    xbmcplugin.endOfDirectory(ADDON_HANDLE, cacheToDisc=False)


def display_movies(movies):
    """Display watched movies as video items."""
    if not movies:
        xbmcgui.Dialog().notification(ADDON_NAME, 'No watched movies found', xbmcgui.NOTIFICATION_INFO)
        xbmcplugin.endOfDirectory(ADDON_HANDLE)
        return
    
    for movie in movies:
        title = movie.get('title', 'Unknown')
        year = movie.get('year', '')
        watched_at = movie.get('watched_at', '')
        
        label = f'{title} ({year})' if year else title
        if watched_at:
            label += f' [Last: {watched_at[:10]}]'
        
        li = xbmcgui.ListItem(label=label)
        li.setInfo('video', {
            'title': title,
            'year': year,
            'premiered': watched_at[:10] if watched_at else ''
        })
        li.setProperty('IsPlayable', 'false')
        
        movie_id = movie.get('ids', {}).get('trakt', '')
        xbmcplugin.addDirectoryItem(ADDON_HANDLE, get_url('movie_detail', id=movie_id, title=title), li, isFolder=True)
    
    xbmcplugin.endOfDirectory(ADDON_HANDLE, cacheToDisc=False)


def display_shows(shows):
    """Display watched TV shows as video items."""
    if not shows:
        xbmcgui.Dialog().notification(ADDON_NAME, 'No watched shows found', xbmcgui.NOTIFICATION_INFO)
        xbmcplugin.endOfDirectory(ADDON_HANDLE)
        return
    
    for show in shows:
        title = show.get('title', 'Unknown')
        year = show.get('year', '')
        episode_count = show.get('episode_count', 0)
        seasons = show.get('seasons', [])
        
        label = f'{title} ({year})' if year else title
        label += f' [{episode_count} episodes]'
        
        li = xbmcgui.ListItem(label=label)
        li.setInfo('video', {
            'title': title,
            'year': year,
            'episode': episode_count
        })
        
        show_id = show.get('ids', {}).get('trakt', '')
        xbmcplugin.addDirectoryItem(ADDON_HANDLE, get_url('show_detail', id=show_id, title=title), li, isFolder=True)
    
    xbmcplugin.endOfDirectory(ADDON_HANDLE, cacheToDisc=False)


def display_movie_detail(movie_id, title):
    """Display movie detail view."""
    li = xbmcgui.ListItem(label=title)
    li.setInfo('video', {'title': title})
    li.setProperty('IsPlayable', 'false')
    xbmcplugin.addDirectoryItem(ADDON_HANDLE, '', li, isFolder=False)
    xbmcplugin.endOfDirectory(ADDON_HANDLE)


def display_show_detail(show_id, title):
    """Display show detail with seasons."""
    trakt = get_trakt_watchlist()
    shows = trakt.get_watched_shows()
    
    # Find the show data
    show_data = None
    for show in shows:
        if str(show.get('ids', {}).get('trakt', '')) == str(show_id):
            show_data = show
            break
    
    if not show_data:
        xbmcplugin.endOfDirectory(ADDON_HANDLE)
        return
    
    seasons = show_data.get('seasons', [])
    for season in seasons:
        season_num = season.get('number', 0)
        ep_count = season.get('episode_count', 0)
        
        if season_num == 0:  # Specials
            label = f'Specials [{ep_count} episodes]'
        else:
            label = f'Season {season_num} [{ep_count} episodes]'
        
        li = xbmcgui.ListItem(label=label)
        li.setInfo('video', {'season': season_num})
        xbmcplugin.addDirectoryItem(ADDON_HANDLE, get_url('season_detail', show=show_id, season=season_num, title=title), li, isFolder=True)
    
    xbmcplugin.setPluginCategory(ADDON_HANDLE, title)
    xbmcplugin.endOfDirectory(ADDON_HANDLE, cacheToDisc=False)


def display_season_detail(show_id, season, title):
    """Display episodes in a season."""
    # For now, just show placeholder episodes
    # In a full implementation, you'd get the actual episode data from Trakt
    for ep in range(1, 13):
        label = f'S{season:02d}E{ep:02d} - Episode {ep}'
        li = xbmcgui.ListItem(label=label)
        li.setInfo('video', {
            'season': season,
            'episode': ep,
            'title': f'Episode {ep}'
        })
        li.setProperty('IsPlayable', 'false')
        xbmcplugin.addDirectoryItem(ADDON_HANDLE, '', li, isFolder=False)
    
    xbmcplugin.setPluginCategory(ADDON_HANDLE, f'{title} - Season {season}')
    xbmcplugin.endOfDirectory(ADDON_HANDLE, cacheToDisc=False)


def router(paramstring):
    """Route commands based on parameters."""
    params = dict(xbmc.parseQuery(paramstring))
    action = params.get('action', '')
    
    if not action:
        build_menu()
        return
    
    trakt = get_trakt_watchlist()
    
    if action == 'movies':
        display_movies(trakt.get_watched_movies())
    
    elif action == 'shows':
        display_shows(trakt.get_watched_shows())
    
    elif action == 'movie_detail':
        display_movie_detail(params.get('id'), params.get('title', 'Unknown'))
    
    elif action == 'show_detail':
        display_show_detail(params.get('id'), params.get('title', 'Unknown'))
    
    elif action == 'season_detail':
        display_season_detail(params.get('show'), int(params.get('season', 1)), params.get('title', ''))
    
    elif action == 'status':
        if trakt.is_configured():
            profile = trakt.get_user_profile()
            if profile:
                xbmcgui.Dialog().ok(ADDON_NAME, f"Connected!\nUsername: {profile.get('username', 'N/A')}")
            else:
                xbmcgui.Dialog().notification(ADDON_NAME, 'Connected to Trakt', xbmcgui.NOTIFICATION_INFO)
        else:
            xbmcgui.Dialog().ok(ADDON_NAME, 'Not configured.\n\nEnter your Trakt Client ID and Secret in settings.')
    
    elif action == 'settings':
        ADDON.openSettings()
        build_menu()
    
    else:
        build_menu()


if __name__ == '__main__':
    router(sys.argv[2][1:] if len(sys.argv) > 2 else '')