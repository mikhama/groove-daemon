# Tasks

## 1. Project Setup
- [x] 1.1 Add `requests` dependency via Poetry
- [x] 1.2 Add `.data/` to `.gitignore`
- [x] 1.3 Create `.data/albums/` directory structure

## 2. Discogs Downloader Implementation
- [x] 2.1 Create `app/discogs_download.py` module
- [x] 2.2 Implement Discogs API search
- [x] 2.3 Display numbered list of search results (artist, title, year, format)
- [x] 2.4 Implement user selection prompt to choose a release
- [x] 2.5 Handle user cancellation (q or empty input)
- [x] 2.6 Fetch full release details for the selected result
- [x] 2.7 Save transformed JSON file in `.data/albums/`
- [x] 2.8 Update CLI to accept single query argument (e.g., "Linkin Park - Papercuts")
- [x] 2.9 Handle API errors and rate limiting gracefully with retries

## 3. Data Transformation
- [x] 3.1 Transform Discogs response to simplified format (id, cover, sides)
- [x] 3.2 Group tracks by side letter from position (A, B, C, D)
- [x] 3.3 Resolve track artist (track artists first, fallback to album artist)
- [x] 3.4 Extract primary image as cover
- [x] 3.5 Warn if any track duration is missing

## 4. Testing
- [ ] 4.1 Test with "Artist - Album" format query
- [ ] 4.2 Test with soundtrack query (e.g., "Stranger Things 4 Soundtrack")
