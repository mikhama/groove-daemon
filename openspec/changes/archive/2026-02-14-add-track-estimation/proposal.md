# Change: Add Keyboard-Based Track Estimation

## Why
The system needs to estimate and display the current track during playback. Until RFID hardware is available, a keyboard-based interface allows manual album selection. Track estimation uses elapsed playback time to calculate which track is currently playing.

## What Changes
- Rename `app/audio_detector.py` to `app/main.py` (entry point)
- Add `app/track_estimator.py` - module to estimate current track based on elapsed time
- Add `app/album_loader.py` - module to load album data from `.data/albums/` and parse durations
- Modify `app/main.py` - integrate keyboard input and track display
- Keyboard controls:
  - Type album ID + Enter during IDLE/STOPPED to load album
  - `d` for next side
  - `a` for previous side
- Display format: `{artist} - {title}` for current track

## Impact
- Affected specs: `track-estimation` (new capability), `audio-detection` (modified - file rename)
- Affected code: `app/audio_detector.py` → `app/main.py` (renamed), `app/track_estimator.py` (new), `app/album_loader.py` (new)
- Dependencies: None new (uses existing album JSON files from discogs-import)
