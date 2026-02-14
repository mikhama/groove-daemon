# Change: Add Discogs Album Downloader Script

## Why
The vinyl playback monitor needs album metadata (artist, album title, track listings with durations) to enable track estimation. Discogs provides a comprehensive database of vinyl releases that can be queried via their public API. Users often don't know the exact artist name (e.g., soundtracks like "Stranger Things 4 Soundtrack"), so an interactive search mode is needed.

## What Changes
- Add `app/discogs_download.py` - standalone script to fetch album info from Discogs API
- Single query interface: `python app/discogs_download.py "Linkin Park - Papercuts"` or `"Stranger Things 4 Soundtrack"`
- Display search results and let user select which release to download
- Transform Discogs response to simplified format: id, cover, sides with tracks (artist, title, duration)
- Group tracks by side letter (A, B, C, D) from position field
- Warn user when track durations are missing (need manual fill)
- Save album metadata as JSON files in `.data/albums/` directory
- Add `.data/` to `.gitignore` to keep local data out of version control
- Add `requests` dependency for HTTP calls

## Impact
- Affected specs: `discogs-import` (new capability)
- Affected code: `app/discogs_download.py` (new file), `.gitignore` (modified)
- New directory: `.data/albums/`
- Dependencies added: `requests` via Poetry
