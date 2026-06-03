# -*- coding: utf-8 -*-
"""
Menu integration for Trakt Watchlist addon.
Provides context menu integration.
"""

import xbmcgui
from resources.lib.trakt_core import get_trakt_watchlist


def build_trakt_menu():
    """Build Trakt-specific menu items."""
    trakt = get_trakt_watchlist()
    status = 'Connected' if trakt.is_configured() else 'Not Connected'
    
    items = [
        (f'Trakt Status: {status}', 'noop', 'DefaultIconInfo.png'),
        ('My Watched Movies', 'RunScript(script.trakt.watchlist,action,movies)', 'DefaultMovieTitle.png'),
        ('My Watched Shows', 'RunScript(script.trakt.watchlist,action,shows)', 'DefaultTVShows.png'),
        ('Settings', 'RunScript(script.trakt.watchlist,action,settings)', 'DefaultAddonSettings.png'),
    ]
    
    return items


def show_trakt_info():
    """Display Trakt account info."""
    trakt = get_trakt_watchlist()
    
    if not trakt.is_configured():
        xbmcgui.Dialog().ok(
            'Trakt Watchlist',
            'Not configured.\n\nEnter your Trakt Client ID and Secret in settings.'
        )
        return
    
    profile = trakt.get_user_profile()
    
    if profile:
        xbmcgui.Dialog().ok('Trakt Account', f"Username: {profile.get('username', 'N/A')}")
    else:
        xbmcgui.Dialog().notification('Trakt Watchlist', 'Connected to Trakt', xbmcgui.NOTIFICATION_INFO)