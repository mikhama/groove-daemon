# Tasks

## 1. Project Restructure
- [x] 1.1 Rename `app/audio_detector.py` to `app/main.py`
- [x] 1.2 Update any imports if needed

## 2. Album Loader Module
- [x] 2.1 Create `app/album_loader.py` module
- [x] 2.2 Implement `load_album(album_id: int)` to load JSON from `.data/albums/`
- [x] 2.3 Implement `parse_duration(duration_str: str)` to convert "M:SS" to seconds
- [x] 2.4 Return structured album data with durations in seconds

## 3. Track Estimator Module
- [x] 3.1 Create `app/track_estimator.py` module
- [x] 3.2 Implement side tracking (current side index, list of sides)
- [x] 3.3 Implement `next_side()` and `prev_side()` methods
- [x] 3.4 Implement `get_current_track(elapsed_seconds: float)` to estimate track
- [x] 3.5 Return side info for display

## 4. Keyboard Input Handler
- [x] 4.1 Add non-blocking keyboard input using `select` (Unix).
- [x] 4.2 Handle album ID input (buffer digits, submit on Enter, display typed input)
- [x] 4.3 Handle `d` for next side
- [x] 4.4 Handle `a` for previous side

## 5. Main Module Integration
- [x] 5.1 Integrate album loader and track estimator into main module
- [x] 5.2 Use session elapsed time for track estimation on current side
- [x] 5.3 Update status display to show current track: "{artist} - {title}"
- [x] 5.4 Show side indicator (e.g., "Side A", "Side B")
- [x] 5.5 Show hint when no album loaded
- [x] 5.6 Auto-advance to next side when playback stops after side duration exceeded

## 6. Testing
- [x] 6.1 Test album loading with existing Linkin Park album
- [x] 6.2 Test side switching (a/d keys)
- [x] 6.3 Test track estimation with manual time progression
