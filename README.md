"# show_my_data_track

A Kodi addon to display your watched movies and TV shows from your Trakt.tv account.

## Features

- View all your watched movies with play counts
- Browse your watched TV shows with episode counts  
- Uses **script.module.trakt** library for API calls (no custom OAuth code needed)
- Simple and lightweight implementation
- Background service for automatic data refresh
- Context menu integration for Trakt actions

## Requirements

- Kodi 19 (Matrix) or higher
- A Trakt.tv account
- Trakt API credentials (Client ID and Client Secret)

## Setup Instructions

### 1. Get Trakt API Credentials

1. Go to [https://trakt.tv/oauth/applications](https://trakt.tv/oauth/applications)
2. Click "Create a new app"
3. Fill in the details:
   - Name: `Kodi Watchlist` (or any name you prefer)
   - Redirect URI: `urn:ietf:wg:oauth:2.0:oob`
4. Click Save
5. Note your **Client ID** and **Client Secret**

### 2. Install the Addon

1. Copy the `plugin.trakt.watchlist` folder to your Kodi addons directory:
   - Linux: `~/.kodi/addons/`
   - macOS: `~/Library/Application Support/Kodi/addons/`
   - Windows: `%APPDATA%\Kodi\addons\`
   - Android: `Android/data/org.xbmc.kodi/files/.kodi/addons/`

2. Restart Kodi or go to Settings > Add-ons > Install from zip

### 3. Configure the Addon

1. Go to Settings > Add-ons > My add-ons > Scripts > Trakt Watchlist
2. Click "Configure"
3. Enter your **Client ID** and **Client Secret**
4. Click "Authorize with Trakt" and follow the on-screen instructions
5. You'll be shown a URL and code to enter on Trakt.tv

## Usage

### Main Menu
- **Watched Movies**: Browse your complete movie watch history
- **Watched TV Shows**: Browse your watched TV shows
- **Sync with Trakt**: Refresh your data from Trakt.tv

### Context Menu
Right-click on any movie or episode to:
- Mark as Watched/Unwatched on Trakt
- Add to Trakt Collection

## How It Works

This addon uses the Trakt.tv API to fetch your watch history:

1. **Authentication**: Uses OAuth device code flow for secure authentication
2. **Token Management**: Automatically refreshes expired access tokens
3. **API Calls**: Fetches watched movies and shows using the `/sync/watched/` endpoints
4. **Caching**: Optional local caching to reduce API calls

## Directory Structure

```
plugin.trakt.watchlist/
├── addon.xml           # Addon manifest (video plugin)
├── default.py          # Main entry point
├── service.py          # Background service
├── icon.png            # Addon icon
├── fanart.jpg          # Addon fanart
└── resources/
    ├── settings.xml    # Settings definitions
    └── lib/
        ├── __init__.py
        └── trakt_core.py   # Trakt API integration
```

## API Endpoints Used

- `GET /sync/watched/movies` - Fetch watched movies
- `GET /sync/watched/shows` - Fetch watched shows  
- `POST /oauth/token` - Token refresh
- `POST /oauth/device/code` - Device authorization
- `GET /users/me` - User profile

## Troubleshooting

### "Not connected to Trakt"
- Make sure you've entered your Client ID and Client Secret
- Click "Authorize with Trakt" and complete the authorization process

### "No watched movies/shows found"
- Verify your Trakt account has watch history
- Check that authorization was completed successfully
- Try clicking "Sync with Trakt" to refresh data

### Token errors
- The addon will automatically refresh expired tokens
- If problems persist, go to settings and re-authorize

## License

This project is provided as-is for personal use." 
