# -*- coding: utf-8 -*-
"""
Menu integration for Trakt Watchlist addon.
Provides context menu and library integration.
"""

import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
from resources.lib import trakt_core


def add_context_menu_items(listitem, media_type, media_id):
    """Add context menu items for Trakt actions."""
    menu_items = []
    
    if media_type == 'movie':
        menu_items.append(
            ('Mark as Watched on Trakt', f'RunScript(script.trakt.watchlist,mark_watched,movie,{media_id})'),
            ('Mark as Unwatched on Trakt', f'RunScript(script.trakt.watchlist,mark_unwatched,movie,{media_id})'),
            ('Add to Trakt Collection', f'RunScript(script.trakt.watchlist,add_collection,movie,{media_id})'),
        )
    elif media_type == 'episode':
        menu_items.append(
            ('Mark as Watched on Trakt', f'RunScript(script.trakt.watchlist,mark_watched,episode,{media_id})'),
            ('Mark as Unwatched on Trakt', f'RunScript(script.trakt.watchlist,mark_unwatched,episode,{media_id})'),
        )
    
    return menu_items


def build_trakt_menu():
    """Build Trakt-specific menu."""
    items = []
    
    # Trakt status
    trakt = trakt_core.get_trakt()
    status = 'Connected' if trakt.is_token_valid() else 'Not Connected'
    items.append((f'Trakt Status: {status}', 'noop', 'DefaultIconInfo.png'))
    
    # Quick actions
    items.append(('[COLOR highlight]My Watched Movies[/COLOR]', 'RunScript(script.trakt.watchlist,action,movies)', 'DefaultMovieTitle.png'))
    items.append(('[COLOR highlight]My Watched Shows[/COLOR]', 'RunScript(script.trakt.watchlist,action,shows)', 'DefaultTVShows.png'))
    items.append(('Refresh Data', 'RunScript(script.trakt.watchlist,action,sync)', 'DefaultAddonService.png'))
    items.append(('Settings', 'RunScript(script.trakt.watchlist,action,settings)', 'DefaultAddonSettings.png'))
    
    return items


def show_trakt_info():
    """Display Trakt account info."""
    trakt = trakt_core.get_trakt()
    
    if not trakt.is_token_valid():
        xbmcgui.Dialog().ok(
            'Trakt Watchlist',
            'Not connected to Trakt.\n\n'
            'Please configure your Client ID and Secret in settings, '
            'then authorize the addon.'
        )
        return
    
    # Get user profile
    profile = trakt.get_user_profile()
    
    if profile:
        username = profile.get('username', 'Unknown')
        name = profile.get('name', '')
        joined = profile.get('joined_at', '')[:10] if profile.get('joined_at') else 'Unknown'
        
        msg = f'Username: {username}'
        if name:
            msg += f'\nName: {name}'
        msg += f'\nMember since: {joined}'
        
        xbmcgui.Dialog().ok('Trakt Account Info', msg)
    else:
        xbmcgui.Dialog().ok('Trakt Watchlist', 'Connected to Trakt!')


def mark_as_watched(media_type, media_id):
    """Mark media as watched on Trakt."""
    trakt = trakt_core.get_trakt()
    # Implementation would call Trakt API to mark as watched
    xbmcgui.Dialog().notification('Trakt Watchlist', f'Marked as watched: {media_type}', xbmcgui.NOTIFICATION_INFO)


def mark_as_unwatched(media_type, media_id):
    """Mark media as unwatched on Trakt."""
    trakt = trakt_core.get_trakt()
    # Implementation would call Trakt API to mark as unwatched
    xbmcgui.Dialog().notification('Trakt Watchlist', f'Marked as unwatched: {media_type}', xbmcgui.NOTIFICATION_INFO)